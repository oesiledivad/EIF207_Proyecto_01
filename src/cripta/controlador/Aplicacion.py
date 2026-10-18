"""Controlador de Aplicación (MVC).
"""

from __future__ import annotations


import struct
from pathlib import Path
from cripta.controlador.ExploracionControlador import ExploracionControlador

from cripta.replay.reproductor import ErrorRegistro
from cripta.adaptadores.Crypt_Data_Source import CryptDataSource, PresupuestoAgotado
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.controlador.GestorPartida import GestorPartida
from cripta.controlador.PartidaControlador import PartidaControlador
from cripta.controlador.InventarioControlador import InventarioControlador
from cripta.controlador.CombateControlador import CombateControlador
from cripta.controlador.EfectosControlador import EfectosControlador

from cripta.controlador.guardado import escribir_partida, leer_partida, restaurar_partida

from cripta.dto.Partida_dto import (
    CriptaResumen,
    DetallesCripta,
    EstadoPartida,
    ResultadoInicio,
    ContenidoSala,
    EnemigoPartida,
    SalaModelo,
)
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.servicio.CriptaService import CriptaService
from cripta.modelo.Simulacion import Simulacion
from cripta.modelo.Combate import esta_vivo
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Puertas import abrir_salida, buscar_llave
from cripta.modelo.Sala import SalaJuego
from cripta.util.Costo_Acciones import costo_accion, calcular_intervalo

# esto me arregla el problema de no poder utilizar dict ni sorted
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Salidas import Salidas

class Aplicacion:
    """Controlador de Aplicación.

    Args:
        data_source: Adaptador de datos (red u offline).
        capacidad_cache: Tope de fichas en memoria (--cache-size, §4.4).
        almacen: Caché persistente en disco (None = desactivada).
    """

    def __init__(self, data_source: CryptDataSource, capacidad_cache: int = 25,
                almacen: AlmacenDisco | None = None, carpeta_logs=None, ruta_puntajes=None, ruta_guardado=None) -> None:
        self._cripta_service = CriptaService(
            data_source, Cache_Fichas(capacidad=capacidad_cache), almacen
        )
        self._gestor = GestorPartida()
        self._bitacora = Bitacora(capacidad=20)
        self._inventario = InventarioControlador(self._gestor, self._bitacora, self._cripta_service)
        self._efectos = EfectosControlador(self._gestor, self._bitacora, self._cripta_service)
        self._combate = CombateControlador(self._gestor, self._bitacora, self._cripta_service, self._efectos)
        self._simulacion: Simulacion | None = None
        self._jugador: Jugador | None = None
        self._exploracion = ExploracionControlador(self)  # Cambio(kyara)

        self._partida = PartidaControlador(self._gestor, self._bitacora, carpeta_logs, ruta_puntajes)
        self.ruta_guardado = Path(ruta_guardado) if ruta_guardado is not None else Path("partida_guardada.bin")
        self._registro_original = None  # registro de replay apartado mientras hay una partida cargada

    #  Selección

    def listar_criptas(self) -> list[CriptaResumen]:
        return self._cripta_service.listar_criptas()

    def previsualizar_cripta(self, cripta_id: str) -> DetallesCripta:
        return self._cripta_service.obtener_detalles(cripta_id)

    def iniciar_partida(
        self,
        nombre_jugador: str,
        semilla: str,
        cripta_id: str,
    ) -> ResultadoInicio:
        try:
            nombre, semilla_efectiva = self._partida.validar_inicio(nombre_jugador, semilla, cripta_id)
        except ValueError as error:
            return ResultadoInicio(ok=False, motivo=str(error))
        if self._registro_original is not None:  # una partida nueva vuelve a grabarse
            self._partida._registro = self._registro_original
            self._registro_original = None

        if self._jugador is not None:
            self._cripta_service.reiniciar_partida()
        try:
            # Si ya se pidió al previsualizar, el servicio lo devuelve sin gastar red.
            detalles = self._cripta_service.obtener_detalles(cripta_id)
        except (PresupuestoAgotado, RuntimeError) as e:
            return ResultadoInicio(ok=False, motivo=f"No se pudieron leer los datos de la cripta: {e}")
        self._cripta_service.fijar_presupuesto(detalles.presupuesto_solicitudes)
        if self._partida.registro is not None:
            try:
                self._cripta_service.obtener_version_catalogo(actualizar=True)
            except (OSError, RuntimeError, ValueError, NotImplementedError) as error:
                return ResultadoInicio(ok=False, motivo=f"No se pudo preparar el registro: {error}")

        self._partida.iniciar(
            detalles, nombre, semilla_efectiva,
            "offline" if self._cripta_service.es_offline() else "red",
        )

        self._bitacora.limpiar()
        self._bitacora.append(Mensaje("sistema", f"Partida iniciada en {cripta_id}."))
        self._bitacora.append(Mensaje("sistema", f"Semilla: {semilla_efectiva}."))
        # §4.4: validar lo persistido ANTES de cargar esqueleto, contenido o fichas.
        self._bitacora.append(Mensaje("sistema", self._cripta_service.preparar_persistencia(detalles)))

        self._jugador, self._simulacion = self._partida.preparar_actores(detalles, semilla_efectiva)

        try:
            esqueleto = self._cripta_service.cargar_esqueleto_salas(cripta_id, detalles.sala_salida)
            self._gestor.estado.salas_conocidas = esqueleto
            self._crear_salas_desde_esqueleto(esqueleto)
            # §2.4: el contenido de la sala inicial debe estar antes de la primera acción.
            # Se pide en el mismo lote que las salas más cercanas (hasta 10).
            self._cargar_lote(detalles.sala_inicial)
        except (PresupuestoAgotado, RuntimeError, ValueError) as e:
            self._gestor.estado.activa = False
            return ResultadoInicio(ok=False, motivo=f"No se pudo cargar la cripta: {e}")

        sala_inicial = self._salas.obtener(detalles.sala_inicial)
        sala_inicial.ultimo_tiempo_visita = 0             # §2.9
        self._combate.activar_sala(sala_inicial, self._simulacion)  # §2.4: enemigos de la sala inicial en t=0
        self._avisar(self._cripta_service.fijar_contenido_visible(sala_inicial))  # §4.4
        self._gestor.refrescar_sala_actual()
        self._sincronizar_estado()

        if self._partida.registro is not None:
            try:
                self._partida.iniciar_registro(
                    detalles, self._cripta_service.obtener_version_catalogo(),
                    semilla_efectiva, nombre, self._cripta_service._cache_fichas.capacidad,
                )
            except OSError as error:
                self._gestor.estado.activa = False
                return ResultadoInicio(ok=False, motivo=f"No se pudo crear el registro: {error}")
        return ResultadoInicio(ok=True, semilla_efectiva=semilla_efectiva)

    

     #  Salas y exploración (delegado a ExploracionControlador)
    @property
    def _salas(self) -> IndiceSalas:
        return self._exploracion.salas

    @_salas.setter
    def _salas(self, valor: IndiceSalas) -> None:
        self._exploracion.salas = valor

    @property
    def _max_id_sala(self) -> int:
        return self._exploracion.max_id_sala

    @_max_id_sala.setter
    def _max_id_sala(self, valor: int) -> None:
        self._exploracion.max_id_sala = valor

    def _crear_salas_desde_esqueleto(self, esqueleto: list[SalaModelo]) -> None:
        self._exploracion.ensamblar_salas(esqueleto)

    def _cargar_lote(self, origen_id: int) -> None:
        self._exploracion.cargar_lote(origen_id)

    def _incorporar_contenido(self, sala: SalaJuego | None, contenido: ContenidoSala) -> None:
        self._exploracion.incorporar_contenido(sala, contenido)

    def _avisar(self, mensaje: str | None) -> None:
        if mensaje is not None:
            self._bitacora.append(Mensaje("sistema", mensaje))

    def _tipos_activos(self) -> list[str]:
        return self._cripta_service.tipos_activos(
            self._gestor.inventario, self._salas, self._salas.obtener(self._jugador.sala))

    #  Ciclo de una acción del jugador (§2.3)

    def _partida_en_curso(self) -> bool:
        return (self._simulacion is not None and self._jugador is not None
                and self._gestor.estado.activa)

    def _accion_jugador(self, nombre_costo: str, ejecutar, argumento=None) -> ResultadoAccion:
        """Plantilla común de toda acción que consume tiempo.

        1. abre el intervalo del historial,
        2. ejecuta la acción (si falla: no consume tiempo y se descarta el intervalo),
        3. programa la próxima acción del jugador y corre los eventos hasta su turno,
        4. cierra el intervalo y sincroniza el estado para la vista.
        """
        if not self._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")

        sala_origen = self._jugador.sala
        if self._gestor.historial.hay_intervalo_abierto():
            self._gestor.descartar_intervalo()
        self._gestor.abrir_intervalo()
        historial = self._gestor.historial
        historial.registrar("azar", [self._simulacion.azar, self._simulacion.azar.getstate()])
        for atributo in ["activa", "derrota", "victoria", "terminada"]:
            historial.registrar("atributo",
                               [self._gestor.estado, atributo, getattr(self._gestor.estado, atributo)])
        actual = self._gestor.inventario.item_actual()
        historial.registrar("seleccion_inventario", actual.instancia_id if actual else None)
        try:
            resultado = ejecutar()
            if not resultado.ok:
                historial.revertir_abierto(self._gestor._aplicar_reversion)
                return resultado
            historial.cambiar(self._gestor.estado, "acciones_ejecutadas",
                              self._gestor.estado.acciones_ejecutadas + 1)
            if esta_vivo(self._jugador):
                self._consumir_tiempo_jugador(nombre_costo)
            self._despues_del_ciclo()
            if nombre_costo == "mover":
                self._partida.comprobar_victoria(sala_origen, argumento, self.resumen_red())
            self._partida.registrar_accion(nombre_costo, argumento)
        except Exception as error:
            anteriores = self._tipos_activos()
            historial.revertir_abierto(self._gestor._aplicar_reversion)
            self._avisar(self._cripta_service.reproteger(anteriores, self._tipos_activos()))
            self._despues_del_ciclo()
            if isinstance(error, ErrorRegistro):
                self._gestor.estado.activa = False
            raise
        self._gestor.cerrar_intervalo()
        if self._gestor.estado.terminada:
            self._partida.guardar_puntaje()
        return resultado

    def _consumir_tiempo_jugador(self, nombre_costo: str) -> None:
        sim = self._simulacion
        tiempo_actual = sim.reloj.tiempo_actual
        # Apéndice B: el rastro de la sala actual se refresca en cada acción del jugador.
        self._exploracion.marcar_rastro(tiempo_actual)

        intervalo = calcular_intervalo(costo_accion(nombre_costo), self._jugador.velocidad)
        sim.agenda.reprogramar(self._jugador, tiempo_actual + intervalo, "accion_actor")

        for texto in sim.avanzar_hasta_turno_jugador(self._jugador, self._salas):
            self._bitacora.append(Mensaje("combate", texto))

    def _despues_del_ciclo(self) -> None:
        self._gestor.estado.sala_actual_id = self._jugador.sala
        self._gestor.refrescar_sala_actual()
        self._sincronizar_estado()
        self._partida.comprobar_derrota(esta_vivo(self._jugador), self.resumen_red())
            
    def _actualizar_vecindad(self) -> None:
        self._exploracion.actualizar_vecindad()



    def _sincronizar_estado(self) -> None:
        estado = self._gestor.estado
        self._actualizar_vecindad()
        self._partida.sincronizar_jugador(self._jugador, self._simulacion)
        sala_actual = self._salas.obtener(self._jugador.sala)
        if sala_actual is not None:
            estado.enemigos = [
                EnemigoPartida(
                    id=e.identificador, nombre=e.nombre, vida=e.vida, vida_max=e.vida_max,
                    ataque=e.ataque, defensa=e.defensa, velocidad=e.velocidad,
                    comportamiento=e.comportamiento,
                )
                for e in sala_actual.enemigos if esta_vivo(e)
            ]
            # Misma lista (alias): recoger/soltar modifican directamente el suelo de la sala.
            estado.objetos_suelo = sala_actual.objetos
        estado.efectos = self._efectos.describir(self._jugador)
    # ---- acción: esperar ----

    def esperar(self) -> ResultadoAccion:
        return self._accion_jugador("esperar", self._ejecutar_espera)

    def _ejecutar_espera(self) -> ResultadoAccion:
        self._bitacora.append(Mensaje("jugador", "Esperás."))
        return ResultadoAccion.exito()

    #  Consultas de juego

    def estado_partida(self) -> EstadoPartida:
        return self._gestor.estado

    def bitacora(self) -> Bitacora:
        return self._bitacora

    def solicitudes_usadas(self) -> int:
        return self._cripta_service.requests_made

    def resumen_red(self) -> str:
        """§5.1: solicitudes realizadas, presupuesto, aciertos y fallos de caché."""
        s = self._cripta_service
        return (f"Red: {s.requests_made}/{self._gestor.estado.presupuesto_solicitudes} solicitudes · "
                f"caché: {s.aciertos_cache} aciertos, {s.fallos_cache} fallos, "
                f"{s.lecturas_disco} lecturas de disco")


        #  Guardado binario (extra de P1)
    def guardar(self, ruta=None) -> ResultadoAccion:
        """Guarda la partida activa. No es una acción del jugador: no consume tiempo."""
        if not self._partida_en_curso():
            return ResultadoAccion.fallo("No hay una partida activa para guardar.")
        destino = Path(ruta) if ruta is not None else self.ruta_guardado
        try:
            escribir_partida(self, destino)
        except (OSError, ValueError) as error:
            return ResultadoAccion.fallo(f"No se pudo guardar: {error}")
        self._bitacora.append(Mensaje("sistema", f"Partida guardada en {destino}."))
        return ResultadoAccion.exito()

    def cargar(self, ruta=None) -> ResultadoAccion:
        """Reemplaza la partida actual por la guardada (misma versión de cripta)."""
        origen = Path(ruta) if ruta is not None else self.ruta_guardado
        try:
            datos = leer_partida(origen)
        except (OSError, ValueError, struct.error) as error:
            return ResultadoAccion.fallo(f"No se pudo leer el guardado: {error}")
        try:
            detalles = self._cripta_service.obtener_detalles(datos.cripta_id)
        except (PresupuestoAgotado, RuntimeError) as error:
            return ResultadoAccion.fallo(f"No se pudo validar la cripta del guardado: {error}")
        if detalles.version != datos.version_cripta:
            return ResultadoAccion.fallo("La cripta cambió de versión desde que se guardó.")

        # Una partida cargada no parte de t=0, así que no se graba en el registro de replay.
        original = self._partida._registro if self._partida._registro is not None else self._registro_original
        self._registro_original = None
        self._partida._registro = None
        resultado = self.iniciar_partida(datos.nombre_jugador, str(datos.semilla), datos.cripta_id)
        self._registro_original = original
        if not resultado.ok:
            return ResultadoAccion.fallo(resultado.motivo)
        try:
            restaurar_partida(self, datos)
        except (ValueError, KeyError) as error:
            return ResultadoAccion.fallo(f"El guardado no coincide con la cripta: {error}")
        self._bitacora.append(Mensaje("sistema", f"Partida cargada de {origen}."))
        return ResultadoAccion.exito()
    
    #  Inventario (delegado a InventarioController; aquí se les da costo de tiempo)

    def recoger(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador("recoger", lambda: self._inventario.recoger(instancia_id), instancia_id)

    def soltar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador("soltar", lambda: self._inventario.soltar(instancia_id, self._jugador), instancia_id)

    def equipar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador("equipar_objeto", lambda: self._inventario.equipar(instancia_id, self._jugador), instancia_id)

    def usar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador(
            "usar_objeto",
            lambda: self._inventario.usar(instancia_id, self._jugador, self._simulacion,
                                          self._efectos),
            instancia_id,
        )

    def usar_pergamino(self) -> ResultadoAccion:
        if not self._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")
        anteriores = self._tipos_activos()
        resultado = self._partida.retroceder()
        if resultado.ok:
            self._avisar(self._cripta_service.reproteger(anteriores, self._tipos_activos()))
            self._despues_del_ciclo()
            self._bitacora.append(Mensaje("efecto", "Usaste un pergamino de retroceso."))
        return resultado

    def siguiente_item(self) -> ResultadoAccion:
        return self._recorrer_inventario(self._inventario.siguiente, "siguiente_item")

    def anterior_item(self) -> ResultadoAccion:
        return self._recorrer_inventario(self._inventario.anterior, "anterior_item")

    def _recorrer_inventario(self, recorrer, nombre: str) -> ResultadoAccion:
        if not self._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")
        return self._inventario.recorrer(recorrer, nombre, self._partida.registrar_accion)

    def vista_inventario(self, criterio: str) -> list:
        return self._inventario.vista_ordenada(criterio)

    def inventario(self):
        """Devuelve el inventario activo o None."""
        return self._gestor.inventario

    #  Acciones de partida

    def mover(self, direccion: str) -> ResultadoAccion:
        return self._exploracion.mover(direccion)

    def abrir(self, direccion: str) -> ResultadoAccion:
        """Abre la puerta de la sala actual en `direccion` (§2.5). Costo 50."""
        return self._exploracion.abrir(direccion)

    abrir_puerta = abrir

    def atacar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador(
            "atacar",
            lambda: self._combate.atacar(instancia_id, self._jugador, self._simulacion, self._salas),
            instancia_id,
        )

    def puntajes(self):
        return self._partida.puntajes()

    @property
    def error_puntaje(self):
        return self._partida.error_puntaje

    def terminar(self) -> None:
        self._partida.terminar(self.resumen_red())
