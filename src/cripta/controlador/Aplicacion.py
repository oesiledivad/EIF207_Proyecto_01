"""Controlador de Aplicación (MVC).
"""

from __future__ import annotations

from cripta.replay.reproductor import ErrorRegistro
from cripta.adaptadores.Crypt_Data_Source import CryptDataSource, PresupuestoAgotado
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.controlador.GestorPartida import GestorPartida
from cripta.controlador.PartidaControlador import PartidaControlador
from cripta.controlador.InventarioControlador import InventarioControlador
from cripta.controlador.CombateControlador import CombateControlador
from cripta.controlador.EfectosControlador import EfectosControlador
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
                 almacen: AlmacenDisco | None = None, carpeta_logs=None, ruta_puntajes=None) -> None:
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
        self._salas: IndiceSalas = IndiceSalas()  # antes: dict[int, SalaJuego]
        self._max_id_sala = 0
        self._partida = PartidaControlador(self._gestor, self._bitacora, carpeta_logs, ruta_puntajes)

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

    #  Salas y red (§4.2)

    def _crear_salas_desde_esqueleto(self, esqueleto: list[SalaModelo]) -> None:
        """Crea TODAS las salas (vacías) apenas llega el esqueleto.

        Así un enemigo activo puede moverse a una sala cuyo contenido aún no
        se pidió, y el rastreador puede consultar el rastro de cualquier vecina.
        """
        self._salas = IndiceSalas()
        self._max_id_sala = 0
        for sala_modelo in esqueleto:
            salidas = Salidas()
            for v in sala_modelo.salidas:
                salidas.agregar(v.direccion, v.sala_id, v.cerrada, v.llave or None, v.cierre_automatico)
            self._salas.insertar(sala_modelo.id, SalaJuego(
                id=sala_modelo.id, nombre=sala_modelo.nombre, salidas=salidas,
                enemigos=[], objetos=[], trampas=[],
            ))
            if sala_modelo.id > self._max_id_sala:
                self._max_id_sala = sala_modelo.id

    def _cargar_lote(self, origen_id: int) -> None:
        """Lote de hasta 10 salas alrededor de `origen_id` (precarga en CriptaService)."""
        self._cripta_service.cargar_lote(self._gestor.estado.cripta_id, self._salas,
                                         self._max_id_sala, origen_id, self._incorporar_contenido)

    def _incorporar_contenido(self, sala: SalaJuego | None, contenido: ContenidoSala) -> None:
        """Incorporar NO activa enemigos (§2.4): quedan dormidos hasta que el jugador entre."""
        if sala is None or sala.contenido_cargado:
            return  # una sala ya cargada no se vuelve a incorporar
        for dto in contenido.enemigos:
            # agregar (no reemplazar): puede haber enemigos activos que ya llegaron caminando
            sala.agregar_enemigo(self._combate.crear_enemigo(dto, sala.id))
        sala.objetos.extend(contenido.objetos)
        for t in contenido.trampas:
            sala.trampas.append(self._efectos.crear_trampa(t))
        sala.contenido_cargado = True
        self._gestor.estado.contenido_cargado.append(sala.id)

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
        sim.agenda.cambiar(self._salas.obtener(self._jugador.sala), "ultimo_tiempo_visita", tiempo_actual)

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
        """Pone al día la vecindad que lee la Vista a partir del Modelo (fuente de verdad).

        Copia el estado vivo de cada puerta (SalaJuego.salidas) y marca si la sala
        vecina tiene enemigos vivos u objetos. O(k * e), k = salidas (máx. 4).
        """
        sala = self._salas.obtener(self._jugador.sala)
        if sala is None:
            return
        for v in self._gestor.estado.vecindad:
            salida = sala.salidas.obtener(v.direccion)
            if salida is not None:
                v.cerrada = salida.cerrada
                v.transitable = not salida.cerrada
                v.llave = salida.llave or ""
                v.cierre_automatico = salida.cierre_automatico
            vecina = self._salas.obtener(v.sala_id)
            if vecina is None:
                continue
            hay_enemigos = False
            for e in vecina.enemigos:
                if esta_vivo(e):
                    hay_enemigos = True
                    break
            v.tiene_enemigos = hay_enemigos
            v.tiene_objetos = len(vecina.objetos) > 0

    def _sincronizar_estado(self) -> None:
        estado = self._gestor.estado
        self._actualizar_vecindad()          # <- NUEVO
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
        anterior = self._gestor.inventario.item_actual()
        resultado = recorrer()
        if resultado.ok:
            try:
                self._partida.registrar_accion(nombre)
            except ErrorRegistro:
                if anterior is not None:
                    self._gestor.inventario.seleccionar(anterior.instancia_id)
                raise
        return resultado

    def vista_inventario(self, criterio: str) -> list:
        return self._inventario.vista_ordenada(criterio)

    def inventario(self):
        """Devuelve el inventario activo o None."""
        return self._gestor.inventario

    #  Acciones de partida

    def mover(self, direccion: str) -> ResultadoAccion:
        if not self._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")

        direccion = direccion.strip().upper()
        sala_actual = self._salas.obtener(self._jugador.sala)
        if sala_actual is None:
            return ResultadoAccion.fallo("Sala actual no cargada.")

        salida = sala_actual.salidas.obtener(direccion)
        if salida is None:
            return ResultadoAccion.fallo("No hay salida en esa dirección.")
        if salida.cerrada:
            return ResultadoAccion.fallo("La puerta está cerrada.")

        destino_id = salida.sala_destino
        # §4.2: el contenido debe estar ANTES de confirmar el movimiento.
        error = self._cripta_service.asegurar_sala_cargada(
            self._gestor.estado.cripta_id, self._salas, self._max_id_sala, destino_id,
            self._incorporar_contenido)
        if error is not None:
            return ResultadoAccion.fallo(f"No se pudo cargar la sala destino: {error}")

        resultado = self._accion_jugador("mover", lambda: self._ejecutar_movimiento(destino_id, direccion), direccion)
        if resultado.ok and self._partida_en_curso():
            self._avisar(self._cripta_service.precargar_alrededor(   # lista para la próxima puerta
                self._gestor.estado.cripta_id, self._salas, self._max_id_sala,
                self._jugador.sala, self._incorporar_contenido))
        return resultado

    def _ejecutar_movimiento(self, destino_id: int, direccion: str) -> ResultadoAccion:
        sala_origen = self._salas.obtener(self._jugador.sala)
        sala_destino = self._salas.obtener(destino_id)
        tiempo_actual = self._simulacion.reloj.tiempo_actual

        self._cripta_service.liberar_contenido_visible(sala_origen)   # deja de ser la sala actual
        self._simulacion.agenda.cambiar(self._jugador, "sala", destino_id)
        self._simulacion.agenda.cambiar(sala_destino, "ultimo_tiempo_visita", tiempo_actual)  # §2.9
        self._combate.activar_sala(sala_destino, self._simulacion)   # §2.4
        self._avisar(self._cripta_service.fijar_contenido_visible(sala_destino))
        self._gestor.estado.objetos_suelo = sala_destino.objetos
        self._bitacora.append(Mensaje("jugador", f"Te mueves al {direccion}: {sala_destino.nombre}."))

        # §2.10: cada trampa armada se activa al entrar, antes del siguiente evento.
        self._efectos.disparar_trampas(sala_destino, self._jugador, self._simulacion)
        return ResultadoAccion.exito()

    
    #kyara
    def abrir(self, direccion: str) -> ResultadoAccion:                                     #NUEVO
        """Abre la puerta de la sala actual en `direccion` (§2.5). Costo 50."""
        direccion = direccion.strip().upper()
        return self._accion_jugador("abrir_puerta", lambda: self._ejecutar_apertura(direccion), direccion)
    abrir_puerta = abrir

    def _ejecutar_apertura(self, direccion: str) -> ResultadoAccion:
        sala = self._salas.obtener(self._jugador.sala)
        if sala is None:
            return ResultadoAccion.fallo("Sala actual no cargada.")
        salida = sala.salidas.obtener(direccion)
        if salida is None:
            return ResultadoAccion.fallo("No hay salida en esa dirección.")
        if not salida.cerrada:
            return ResultadoAccion.fallo("Esa puerta ya está abierta.")
        if not salida.llave:
            return ResultadoAccion.fallo("Esa puerta no se abre con llave.")
        inv = self._gestor.inventario
        llave = buscar_llave(inv.items(), salida.llave) if inv is not None else None
        if llave is None:
            return ResultadoAccion.fallo("No tienes la llave correcta.")

        tiempo = self._simulacion.reloj.tiempo_actual
        abrir_salida(salida, tiempo, self._simulacion.agenda)
        self._bitacora.append(Mensaje("jugador", f"Abres la puerta {direccion} con {llave.nombre}."))
        return ResultadoAccion.exito()



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
