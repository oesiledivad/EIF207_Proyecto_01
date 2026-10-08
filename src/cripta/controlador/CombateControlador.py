"""Controlador de combate (P2): creación y activación de enemigos, ataques,
muerte y botín (§2.4, §2.6).

No guarda estado del juego: recibe en cada llamada el jugador, la
simulación y el índice de salas que le pasa Aplicacion.
"""

from __future__ import annotations

from cripta.controlador.EfectosControlador import EfectosControlador
from cripta.controlador.GestorPartida import GestorPartida
from cripta.dto.Partida_dto import EnemigoPartida, ObjetoSuelo
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.estructuras.Ordenamientos import ordenar
from cripta.modelo.Combate import aplicar_danio, calcular_danio, esta_vivo, procesar_muerte
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.enemigos.Errante import Errante
from cripta.modelo.enemigos.Guardian import Guardian
from cripta.modelo.enemigos.Rastreador import Rastreador
from cripta.servicio.CriptaService import CriptaService
from cripta.util.Costo_Acciones import calcular_intervalo, costo_accion


class CombateControlador:
    def __init__(self, gestor: GestorPartida, bitacora: Bitacora, servicio: CriptaService,
                 efectos: EfectosControlador) -> None:
        self._gestor = gestor
        self._bitacora = bitacora
        self._servicio = servicio
        self._efectos = efectos

    #  Creación y activación (§2.4)

    @staticmethod
    def crear_enemigo(dto: EnemigoPartida, sala_id: int):
        """Instancia dormida: copia las estadísticas de la ficha (§2.2)."""
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
        enemigo.nombre = dto.nombre or dto.id
        enemigo.tipo = dto.tipo
        enemigo.suelta = list(dto.suelta)
        enemigo.regeneracion_objetivo = dto.regeneracion  # None si no regenera
        return enemigo

    def activar_sala(self, sala: SalaJuego, simulacion) -> None:
        """Activa los enemigos dormidos, en orden ascendente de id de instancia."""
        dormidos = [e for e in sala.enemigos if esta_vivo(e) and e._proximo_evento is None]
        for enemigo in ordenar(dormidos, key=lambda e: e.identificador):
            self.activar_enemigo(enemigo, simulacion)

    def activar_enemigo(self, enemigo, simulacion) -> None:
        agenda = simulacion.agenda
        tiempo_actual = simulacion.reloj.tiempo_actual
        # §2.4: primera acción = acción base de costo 100 desde el reloj actual.
        intervalo = calcular_intervalo(costo_accion("esperar"), enemigo.velocidad)
        evento = agenda.insertar(tiempo_actual + intervalo, enemigo, "accion_actor")
        agenda.cambiar(enemigo, "_proximo_evento", evento)
        agenda.cambiar(enemigo, "tiempo_siguiente", evento.tiempo_siguiente)
        self._fijar([enemigo.tipo])  # enemigo activo: su ficha está en uso (§4.4)
        self._efectos.iniciar_regeneracion(enemigo, simulacion)

    #  Ataque, muerte y botín (§2.6)

    def atacar(self, instancia_id: str, jugador, simulacion, salas) -> ResultadoAccion:
        sala_actual = salas.obtener(jugador.sala)
        if sala_actual is None:
            return ResultadoAccion.fallo("Sala actual no cargada.")

        enemigo = next(
            (e for e in sala_actual.enemigos if e.identificador == instancia_id and esta_vivo(e)),
            None,
        )
        if enemigo is None:
            return ResultadoAccion.fallo("Ese enemigo no está aquí.")

        dano = calcular_danio(jugador, enemigo, simulacion.azar)
        aplicar_danio(enemigo, dano, simulacion.agenda)
        self._bitacora.append(Mensaje("combate", f"Atacás a {enemigo.etiqueta} por {dano}."))

        if not esta_vivo(enemigo):
            self._matar(enemigo, sala_actual, simulacion)
        return ResultadoAccion.exito()

    def _matar(self, enemigo, sala: SalaJuego, simulacion) -> None:
        """Cancela sus eventos, lo saca de la sala y deja su botín en el suelo."""
        historial = self._gestor.historial
        historial.cambiar(self._gestor.estado, "enemigos_derrotados",
                          self._gestor.estado.enemigos_derrotados + 1)
        self._bitacora.append(Mensaje("combate", f"{enemigo.etiqueta} muere."))
        procesar_muerte(enemigo, simulacion.agenda)  # acción, regeneración, veneno, velocidad
        sala.quitar_enemigo(enemigo, historial)
        self._servicio.liberar_fichas([enemigo.tipo])

        if not enemigo.suelta:
            return
        # El botín queda en el suelo de la sala actual: sus fichas pasan a estar en uso.
        self._fijar(enemigo.suelta)
        nombres: list[str] = []
        for posicion, tipo in enumerate(enemigo.suelta):
            ficha = self._servicio.obtener_ficha(tipo)
            nombre = ficha.nombre if ficha is not None else tipo
            objeto = ObjetoSuelo(
                id=f"botin-{enemigo.identificador}-{posicion}", nombre=nombre, tipo_id=tipo,
            )
            if ficha is not None and ficha.clase == "pergamino_retroceso":
                sala.objetos.append(objeto)  # §2.11: los pergaminos quedan fuera del retroceso
            else:
                historial.agregar(sala.objetos, objeto)
            nombres.append(nombre)
        self._bitacora.append(Mensaje("combate", f"{enemigo.etiqueta} deja caer: {', '.join(nombres)}."))

    #  Interno

    def _fijar(self, tipos: list[str]) -> None:
        error = self._servicio.fijar_seguro(tipos)
        if error is not None:
            self._bitacora.append(Mensaje("sistema", error))
