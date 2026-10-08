"""Controlador de Aplicación (MVC).
"""

from __future__ import annotations

import random

from cripta.replay.reproductor import ErrorRegistro
from cripta.adaptadores.Crypt_Data_Source import CryptDataSource, PresupuestoAgotado
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.controlador.GestorPartida import GestorPartida
from cripta.controlador.PartidaControlador import PartidaControlador
from cripta.controlador.InventarioControlador import InventarioControlador
from cripta.dto.Partida_dto import (
    CriptaResumen,
    DetallesCripta,
    EstadoPartida,
    ResultadoInicio,
    ContenidoSala,
    EnemigoPartida,
    ObjetoSuelo,
    SalaModelo,
)
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.servicio.CriptaService import CriptaService, MAX_POR_LOTE
from cripta.modelo.Simulacion import Simulacion
from cripta.modelo.Combate import esta_vivo, calcular_danio, aplicar_danio, procesar_muerte
from cripta.modelo.Efectos import (
    activar_regeneracion,
    aplicar_modificador_velocidad,
    cancelar_veneno,
    curar,
    disparar_trampa,
    encender_antorcha,
)
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.enemigos.Guardian import Guardian
from cripta.modelo.enemigos.Errante import Errante
from cripta.modelo.enemigos.Rastreador import Rastreador
from cripta.util.Costo_Acciones import costo_accion, calcular_intervalo

# esto me arregla el problema de no poder utilizar dict ni sorted
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Salidas import Salidas
from cripta.estructuras.Ordenamientos import ordenar
from cripta.modelo.Trampa import TrampaJuego

def _generar_semilla() -> int:
    return random.SystemRandom().randint(1, 2**31 - 1)

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
        nombre = nombre_jugador.strip()
        if not nombre:
            return ResultadoInicio(
                ok=False,
                motivo="El nombre del jugador no puede estar vacío.",
            )
        if not cripta_id:
            return ResultadoInicio(
                ok=False,
                motivo="Debes seleccionar una cripta.",
            )

        semilla_txt = semilla.strip()
        if semilla_txt:
            if not semilla_txt.isdigit():
                return ResultadoInicio(
                    ok=False,
                    motivo="La semilla debe ser un número entero o quedar vacía.",
                )
            semilla_efectiva = int(semilla_txt)
        else:
            semilla_efectiva = _generar_semilla()

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

        self._simulacion = Simulacion(semilla_efectiva, self._gestor.historial)
        self._jugador = Jugador(
            identificador="jugador", vida=detalles.jugador_vida_max, vida_max=detalles.jugador_vida_max,
            ataque=detalles.jugador_ataque, defensa=detalles.jugador_defensa,
            velocidad=detalles.jugador_velocidad, sala=detalles.sala_inicial,
            tiempo_siguiente=0, inventario_max=detalles.inventario_max,
        )
        # §2.4: la primera acción del jugador está programada en t=0.
        evento_inicial = self._simulacion.agenda.insertar(0, self._jugador, "accion_actor")
        self._jugador._proximo_evento = evento_inicial

        try:
            esqueleto = self._cripta_service.cargar_esqueleto_salas(cripta_id, detalles.sala_salida)
            self._gestor.estado.salas_conocidas = esqueleto
            self._crear_salas_desde_esqueleto(esqueleto)
            # §2.4: el contenido de la sala inicial debe estar antes de la primera acción.
            # Se pide en el mismo lote que las salas más cercanas (hasta 10).
            self._cargar_lote(self._salas_a_precargar(detalles.sala_inicial))
        except (PresupuestoAgotado, RuntimeError, ValueError) as e:
            self._gestor.estado.activa = False
            return ResultadoInicio(ok=False, motivo=f"No se pudo cargar la cripta: {e}")

        sala_inicial = self._salas.obtener(detalles.sala_inicial)
        sala_inicial.ultimo_tiempo_visita = 0             # §2.9
        self._activar_sala(sala_inicial)                  # §2.4: enemigos de la sala inicial en t=0
        self._fijar_contenido_visible(sala_inicial)       # §4.4: suelo y trampas de la sala actual
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
                salidas.agregar(v.direccion, v.sala_id, v.cerrada)
            self._salas.insertar(sala_modelo.id, SalaJuego(
                id=sala_modelo.id, nombre=sala_modelo.nombre, salidas=salidas,
                enemigos=[], objetos=[], trampas=[],
            ))
            if sala_modelo.id > self._max_id_sala:
                self._max_id_sala = sala_modelo.id

    def _salas_a_precargar(self, origen_id: int) -> list[int]:
        """BFS desde `origen_id` por el esqueleto: las 10 salas sin contenido más cercanas.

        El origen va primero si falta. Cuesta O(salas visitadas) y se corta al
        juntar 10. Usa una lista de bool indexada por id (no set/dict).
        """
        visitado = [False] * (self._max_id_sala + 1)
        cola = [origen_id]
        visitado[origen_id] = True
        i = 0
        elegidas: list[int] = []
        while i < len(cola) and len(elegidas) < MAX_POR_LOTE:
            sala = self._salas.obtener(cola[i])
            i += 1
            if sala is None:
                continue
            if not sala.contenido_cargado:
                elegidas.append(sala.id)
            for salida in sala.salidas:
                destino = salida.sala_destino
                if 0 <= destino <= self._max_id_sala and not visitado[destino]:
                    visitado[destino] = True
                    cola.append(destino)
        return elegidas

    def _necesita_precarga(self, sala_id: int) -> bool:
        """True si la sala o alguna vecina directa todavía no tiene contenido. O(4)."""
        sala = self._salas.obtener(sala_id)
        if sala is None:
            return False
        if not sala.contenido_cargado:
            return True
        for salida in sala.salidas:
            vecina = self._salas.obtener(salida.sala_destino)
            if vecina is not None and not vecina.contenido_cargado:
                return True
        return False

    def _cargar_lote(self, sala_ids: list[int]) -> None:
        """Pide el contenido y lo incorpora en el orden pedido (determinista).

        Incorporar NO activa enemigos (§2.4): quedan dormidos hasta que el
        jugador entre a la sala. Esperar la red nunca mueve el reloj virtual.
        """
        if not sala_ids:
            return
        contenidos = self._cripta_service.cargar_contenido_salas(self._gestor.estado.cripta_id, sala_ids)
        for sala_id, contenido in contenidos:
            self._incorporar_contenido(self._salas.obtener(sala_id), contenido)

    def _incorporar_contenido(self, sala: SalaJuego | None, contenido: ContenidoSala) -> None:
        if sala is None or sala.contenido_cargado:
            return  # una sala ya cargada no se vuelve a incorporar
        for dto in contenido.enemigos:
            # agregar (no reemplazar): puede haber enemigos activos que ya llegaron caminando
            sala.agregar_enemigo(self._crear_enemigo(dto, sala.id))
        sala.objetos.extend(contenido.objetos)
        for t in contenido.trampas:
            sala.trampas.append(TrampaJuego(
                instancia=t.id, armada=t.activa, dano=t.dano,
                rearme=t.rearme, efecto=t.efecto, tipo=t.tipo,
            ))
        sala.contenido_cargado = True
        self._gestor.estado.contenido_cargado.append(sala.id)

    def _asegurar_sala_cargada(self, sala_id: int) -> str | None:
        """Garantiza el contenido antes de confirmar un movimiento. Devuelve error o None."""
        sala = self._salas.obtener(sala_id)
        if sala is None:
            return f"La sala {sala_id} no existe en el esqueleto."
        if sala.contenido_cargado:
            return None
        try:
            self._cargar_lote(self._salas_a_precargar(sala_id))  # sala_id va primero en el lote
        except (PresupuestoAgotado, RuntimeError) as e:
            return str(e)
        return None

    def _precargar_alrededor(self, sala_id: int) -> None:
        """Precarga anticipada: si falta alguna vecina, pide un lote de hasta 10 salas.

        Es opcional: si no hay presupuesto o falla la red, solo se informa.
        """
        if not self._necesita_precarga(sala_id):
            return
        try:
            self._cargar_lote(self._salas_a_precargar(sala_id))
        except PresupuestoAgotado as e:
            self._bitacora.append(Mensaje("sistema", f"Precarga omitida: {e}"))
        except RuntimeError as e:
            self._bitacora.append(Mensaje("sistema", f"Precarga fallida: {e}"))

    #  Fichas en uso (§4.4)

    def _fijar_seguro(self, tipos: list[str]) -> None:
        """Protege fichas en caché; si hubiera que traerlas y no se puede, solo se avisa."""
        try:
            self._cripta_service.fijar_fichas(tipos)
        except (PresupuestoAgotado, RuntimeError) as e:
            self._bitacora.append(Mensaje("sistema", f"No se pudo proteger fichas: {e}"))

    @staticmethod
    def _tipos_visibles(sala: SalaJuego) -> list[str]:
        tipos = [o.tipo_id or o.id for o in sala.objetos]
        for t in sala.trampas:
            tipos.append(t.tipo)
        return tipos

    def _fijar_contenido_visible(self, sala: SalaJuego) -> None:
        """Objetos del suelo y trampas de la sala actual quedan protegidos."""
        self._fijar_seguro(self._tipos_visibles(sala))

    def _liberar_contenido_visible(self, sala: SalaJuego) -> None:
        self._cripta_service.liberar_fichas(self._tipos_visibles(sala))

    #  Enemigos

    def _activar_sala(self, sala: SalaJuego) -> None:
        """§2.4: activa los enemigos dormidos, en orden ascendente de id de instancia."""
        dormidos = [e for e in sala.enemigos if esta_vivo(e) and e._proximo_evento is None]
        for enemigo in ordenar(dormidos, key=lambda e: e.identificador):
            self._activar_enemigo(enemigo)

    def _crear_enemigo(self, dto: EnemigoPartida, sala_id: int):
        match dto.comportamiento:
            case "guardián" | "guardian":
                clase = Guardian
            case "errante":
                clase = Errante
            case "rastreador":
                clase = Rastreador
            case otro:
                raise ValueError(f"Comportamiento desconocido: {otro}")
        enemigo = clase(
            identificador=dto.id, vida=dto.vida, vida_max=dto.vida_max or dto.vida,
            ataque=dto.ataque, defensa=dto.defensa, velocidad=dto.velocidad,
            sala=sala_id, tiempo_siguiente=None, comportamiento=dto.comportamiento,
        )
        enemigo.tipo = dto.tipo
        enemigo.suelta = list(dto.suelta)
        enemigo.regeneracion_objetivo = dto.regeneracion  # None si no regenera
        return enemigo

    def _activar_enemigo(self, enemigo) -> None:
        assert self._simulacion is not None
        tiempo_actual = self._simulacion.reloj.tiempo_actual
        # §2.4: primera acción = acción base de costo 100 desde el reloj actual.
        intervalo = calcular_intervalo(costo_accion("esperar"), enemigo.velocidad)
        evento = self._simulacion.agenda.insertar(tiempo_actual + intervalo, enemigo, "accion_actor")
        self._simulacion.agenda.cambiar(enemigo, "_proximo_evento", evento)
        self._simulacion.agenda.cambiar(enemigo, "tiempo_siguiente", evento.tiempo_siguiente)
        self._fijar_seguro([enemigo.tipo])  # enemigo activo: su ficha está en uso

        if enemigo.regeneracion_objetivo:
            activar_regeneracion(enemigo, enemigo.regeneracion_objetivo, tiempo_actual, self._simulacion.agenda)

    def _matar_enemigo(self, enemigo, sala: SalaJuego) -> None:
        """Muerte (§2.6): cancela sus eventos, lo saca de la sala y deja su botín."""
        self._gestor.historial.cambiar(self._gestor.estado, "enemigos_derrotados",
                                      self._gestor.estado.enemigos_derrotados + 1)
        self._bitacora.append(Mensaje("combate", f"{enemigo.identificador} muere."))
        procesar_muerte(enemigo, self._simulacion.agenda)  # acción, regeneración, veneno, velocidad
        sala.quitar_enemigo(enemigo, self._gestor.historial)
        self._cripta_service.liberar_fichas([enemigo.tipo])

        if enemigo.suelta:
            # El botín queda en el suelo de la sala actual: sus fichas pasan a estar en uso.
            self._fijar_seguro(enemigo.suelta)
            nombres: list[str] = []
            for posicion, tipo in enumerate(enemigo.suelta):
                ficha = self._cripta_service.obtener_ficha(tipo)
                nombre = ficha.nombre if ficha is not None else tipo
                objeto = ObjetoSuelo(
                    id=f"botin-{enemigo.identificador}-{posicion}", nombre=nombre, tipo_id=tipo,
                )
                if ficha is not None and ficha.clase == "pergamino_retroceso":
                    sala.objetos.append(objeto)
                else:
                    self._gestor.historial.agregar(sala.objetos, objeto)
                nombres.append(nombre)
            self._bitacora.append(Mensaje("combate", f"{enemigo.identificador} deja caer: {', '.join(nombres)}."))

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
        historial.registrar("azar", (self._simulacion.azar, self._simulacion.azar.getstate()))
        for atributo in ("activa", "derrota", "victoria", "terminada"):
            historial.registrar("atributo",
                               (self._gestor.estado, atributo, getattr(self._gestor.estado, atributo)))
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
            self._cripta_service.liberar_fichas(anteriores)
            self._fijar_seguro(self._tipos_activos())
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

    def _sincronizar_estado(self) -> None:
        estado = self._gestor.estado
        estado.reloj_virtual = self._simulacion.reloj.tiempo_actual
        estado.jugador_vida = self._jugador.vida
        estado.jugador_ataque = self._jugador.ataque
        estado.jugador_defensa = self._jugador.defensa
        estado.jugador_velocidad = self._jugador.velocidad
        sala_actual = self._salas.obtener(self._jugador.sala)
        if sala_actual is not None:
            estado.enemigos = [
                EnemigoPartida(
                    id=e.identificador, nombre=e.identificador, vida=e.vida, vida_max=e.vida_max,
                    ataque=e.ataque, defensa=e.defensa, velocidad=e.velocidad,
                    comportamiento=e.comportamiento,
                )
                for e in sala_actual.enemigos if esta_vivo(e)
            ]
            # Misma lista (alias): recoger/soltar modifican directamente el suelo de la sala.
            estado.objetos_suelo = sala_actual.objetos
        efectos: list[str] = []
        if self._jugador.evento_veneno is not None:
            efectos.append(f"Envenenado (-{self._jugador.dano_veneno}/pulso hasta t={self._jugador.fin_veneno})")
        if self._jugador.evento_fin_velocidad is not None:
            efectos.append(f"Velocidad alterada ({self._jugador.velocidad})")
        if self._jugador.antorcha_encendida:
            efectos.append("Antorcha encendida")
        estado.efectos = efectos

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
        return self._accion_jugador("usar_objeto", lambda: self._usar_objeto(instancia_id), instancia_id)

    def _tipos_activos(self) -> list[str]:
        tipos = [item.tipo_id for item in self._gestor.inventario.items()]
        for sala in self._salas._datos:
            if sala is not None:
                tipos.extend(e.tipo for e in sala.enemigos
                             if esta_vivo(e) and e._proximo_evento is not None)
        tipos.extend(self._tipos_visibles(self._salas.obtener(self._jugador.sala)))
        return tipos

    def usar_pergamino(self) -> ResultadoAccion:
        if not self._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")
        anteriores = self._tipos_activos()
        resultado = self._partida.retroceder()
        if resultado.ok:
            self._cripta_service.liberar_fichas(anteriores)
            self._fijar_seguro(self._tipos_activos())
            self._despues_del_ciclo()
            self._bitacora.append(Mensaje("efecto", "Usaste un pergamino de retroceso."))
        return resultado

    def siguiente_item(self) -> ResultadoAccion:
        resultado = self._inventario.siguiente()
        if resultado.ok:
            self._partida.registrar_accion("siguiente_item")
        return resultado

    def anterior_item(self) -> ResultadoAccion:
        resultado = self._inventario.anterior()
        if resultado.ok:
            self._partida.registrar_accion("anterior_item")
        return resultado

    def vista_inventario(self, criterio: str) -> list:
        return self._inventario.vista_ordenada(criterio)

    def inventario(self):
        """Devuelve el inventario activo o None."""
        return self._gestor.inventario

    def _usar_objeto(self, instancia_id: str) -> ResultadoAccion:
        """Efectos de objetos consumibles (§2.7, §2.10)."""
        inv = self._gestor.inventario
        item = inv.buscar_por_id(instancia_id) if inv is not None else None
        if item is None:
            return ResultadoAccion.fallo("No tienes ese objeto.")

        try:
            ficha = self._cripta_service.obtener_ficha_garantizada(item.tipo_id)
        except (PresupuestoAgotado, RuntimeError) as e:
            return ResultadoAccion.fallo(f"No se pudo resolver {item.nombre}: {e}")
        if ficha is None:
            return ResultadoAccion.fallo(f"Ficha desconocida: {item.tipo_id}")

        jugador = self._jugador
        tiempo = self._simulacion.reloj.tiempo_actual
        agenda = self._simulacion.agenda

        match ficha.clase:
            case "pocion":
                partes: list[str] = []
                if ficha.cura:
                    partes.append(f"recuperás {curar(jugador, ficha.cura, agenda)} de vida")
                if ficha.modificador_velocidad and ficha.duracion:
                    aplicar_modificador_velocidad(jugador, ficha.modificador_velocidad,
                                                  ficha.duracion, tiempo, agenda)
                    partes.append(f"tu velocidad pasa a {jugador.velocidad} por {ficha.duracion}")
                if not partes:
                    return ResultadoAccion.fallo("Esa poción no tiene efecto.")
                texto = f"Bebés {ficha.nombre}: {', '.join(partes)}."
            case "antidoto":
                if jugador.evento_veneno is None:
                    return ResultadoAccion.fallo("No estás envenenado.")
                cancelar_veneno(jugador, agenda)
                texto = f"Usás {ficha.nombre}: el veneno desaparece."
            case "antorcha":
                texto = encender_antorcha(jugador, ficha.duracion, tiempo, agenda)
            case "llave":
                return ResultadoAccion.fallo("Las llaves no se usan: sirven para abrir puertas.")
            case "arma" | "armadura":
                return ResultadoAccion.fallo("Ese objeto se equipa, no se usa.")
            case "pergamino_retroceso":
                return ResultadoAccion.fallo("Usá la acción de pergamino de retroceso.")
            case otra:
                return ResultadoAccion.fallo(f"No se puede usar un objeto de clase {otra}.")

        self._inventario.consumir(item)
        self._bitacora.append(Mensaje("jugador", texto))
        return ResultadoAccion.exito()

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
        error = self._asegurar_sala_cargada(destino_id)
        if error is not None:
            return ResultadoAccion.fallo(f"No se pudo cargar la sala destino: {error}")

        resultado = self._accion_jugador("mover", lambda: self._ejecutar_movimiento(destino_id, direccion), direccion)
        if resultado.ok and self._partida_en_curso():
            self._precargar_alrededor(self._jugador.sala)  # lista para la próxima puerta
        return resultado

    def _ejecutar_movimiento(self, destino_id: int, direccion: str) -> ResultadoAccion:
        sala_origen = self._salas.obtener(self._jugador.sala)
        sala_destino = self._salas.obtener(destino_id)
        tiempo_actual = self._simulacion.reloj.tiempo_actual

        self._liberar_contenido_visible(sala_origen)   # deja de ser la sala actual
        self._simulacion.agenda.cambiar(self._jugador, "sala", destino_id)
        self._simulacion.agenda.cambiar(sala_destino, "ultimo_tiempo_visita", tiempo_actual)  # §2.9
        self._activar_sala(sala_destino)                  # §2.4
        self._fijar_contenido_visible(sala_destino)
        self._gestor.estado.objetos_suelo = sala_destino.objetos
        self._bitacora.append(Mensaje("jugador", f"Te mueves al {direccion}: {sala_destino.nombre}."))

        # §2.10: cada trampa armada se activa al entrar, antes del siguiente evento.
        for trampa in sala_destino.trampas:
            if trampa.armada:
                texto = disparar_trampa(trampa, self._jugador, tiempo_actual, self._simulacion.agenda)
                self._bitacora.append(Mensaje("combate", texto))
                if not esta_vivo(self._jugador):
                    break
        return ResultadoAccion.exito()

    def atacar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador("atacar", lambda: self._ejecutar_ataque(instancia_id), instancia_id)

    def _ejecutar_ataque(self, instancia_id: str) -> ResultadoAccion:
        sala_actual = self._salas.obtener(self._jugador.sala)
        if sala_actual is None:
            return ResultadoAccion.fallo("Sala actual no cargada.")

        enemigo = next(
            (e for e in sala_actual.enemigos if e.identificador == instancia_id and esta_vivo(e)),
            None,
        )
        if enemigo is None:
            return ResultadoAccion.fallo("Ese enemigo no está aquí.")

        dano = calcular_danio(self._jugador, enemigo, self._simulacion.azar)
        aplicar_danio(enemigo, dano, self._simulacion.agenda)
        self._bitacora.append(Mensaje("combate", f"Atacás a {enemigo.identificador} por {dano}."))

        if not esta_vivo(enemigo):
            self._matar_enemigo(enemigo, sala_actual)
        return ResultadoAccion.exito()

    def puntajes(self):
        return self._partida.puntajes()

    @property
    def error_puntaje(self):
        return self._partida.error_puntaje

    def terminar(self) -> None:
        self._partida.terminar(self.resumen_red())
