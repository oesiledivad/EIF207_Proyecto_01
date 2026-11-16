"""Viaje automático «ir a» (Parte II, §3.4).

Lleva al jugador a una sala explorada con pasos ordinarios: cada paso es una
llamada a `Aplicacion.mover`, así consume tiempo, corre los eventos del reloj,
queda en `partida.log` y lo revierte el pergamino como cualquier movimiento.
La ruta se calcula solo con el conocimiento del jugador y se recalcula antes de
cada paso (FR-026). El estado del viaje NO es estado del juego: no se guarda ni
entra al historial.

Complejidad:
    iniciar / avanzar: una búsqueda de rutas, O((V + A) log V) sobre lo explorado
"""

from __future__ import annotations

from cripta.dto.Conocimiento_dto import ResultadoViaje
from cripta.estructuras.Bitacora import Mensaje
from cripta.modelo.Conocimiento import EXPLORADA
from cripta.modelo.Rutas import BuscadorRutas

MENSAJE_PARTIDA_INACTIVA = "La partida no está activa."
MENSAJE_NO_EXISTE = "La sala indicada no existe."
MENSAJE_NO_EXPLORADA = "Solo puedes ir a una sala que ya exploraste."
MENSAJE_SALA_ACTUAL = "Ya estás en esa sala."
MENSAJE_SIN_RUTA = "No hay ruta conocida hacia esa sala."


class ViajeControlador:
    def __init__(self, app) -> None:
        self._app = app
        self.destino = -1
        self.activo = False
        self.pasos = 0
        self.en_paso = False   # verdadero mientras `avanzar` llama a `mover`
        self.motivo = ""
        self._buscador: BuscadorRutas | None = None

    # Utilidades

    def _buscar(self, origen: int):
        """Recalcula con el conocimiento vigente y devuelve el primer paso, o nada."""
        app = self._app
        conocimiento = app._exploracion.conocimiento
        if self._buscador is None or len(self._buscador.marca) != len(conocimiento.estado_sala):
            self._buscador = BuscadorRutas(len(conocimiento.estado_sala))
        sala = app._salas.obtener(origen)
        if sala is None:
            return None
        self._buscador.distancias_hacia(self.destino, app._exploracion.entrantes,
                                        conocimiento.salida_usable, origen)
        return self._buscador.elegir_paso(origen, sala.salidas, conocimiento.salida_usable)

    def _rechazar(self, texto: str) -> ResultadoViaje:
        """Orden rechazada: mensaje en la bitácora y nada más (sin tiempo, sin registro)."""
        self._app._bitacora.append(Mensaje("viaje", texto))
        return ResultadoViaje(ok=False, activo=False, motivo="", mensaje=texto)

    def _detener(self, motivo: str, texto: str, ok: bool = False) -> ResultadoViaje:
        """Detiene el viaje y escribe exactamente un mensaje con el motivo (FR-031)."""
        self.activo = False
        self.motivo = motivo
        self._app._bitacora.append(Mensaje("viaje", texto))
        return ResultadoViaje(ok=ok, activo=False, motivo=motivo, mensaje=texto)

    # Operaciones

    def iniciar(self, destino) -> ResultadoViaje:
        """Acepta o rechaza la orden `ir a destino` sin consumir tiempo (FR-019 a FR-022)."""
        app = self._app
        if not app._partida_en_curso():
            return self._rechazar(MENSAJE_PARTIDA_INACTIVA)
        conocimiento = app._exploracion.conocimiento
        if (not isinstance(destino, int) or isinstance(destino, bool)
                or not 0 <= destino < len(conocimiento.estado_sala)):
            return self._rechazar(MENSAJE_NO_EXISTE)
        if conocimiento.estado(destino) != EXPLORADA:   # no se distingue desconocida de avistada
            return self._rechazar(MENSAJE_NO_EXPLORADA)
        if destino == app._jugador.sala:
            return self._rechazar(MENSAJE_SALA_ACTUAL)
        self.destino = destino
        if self._buscar(app._jugador.sala) is None:
            return self._rechazar(MENSAJE_SIN_RUTA)
        self.activo = True
        self.pasos = 0
        self.motivo = ""
        return ResultadoViaje(ok=True, activo=True)

    def avanzar(self) -> ResultadoViaje:
        """Da exactamente un paso, o detiene el viaje (FR-025, FR-026, FR-027)."""
        app = self._app
        if not self.activo:
            return ResultadoViaje(ok=False, activo=False, motivo=self.motivo)
        if not app._partida_en_curso():
            return self._detener("partida_terminada", "Viaje detenido: la partida terminó.")
        paso = self._buscar(app._jugador.sala)
        if paso is None:
            return self._detener("sin_ruta", "Viaje detenido: ya no existe una ruta conocida.")
        self.en_paso = True
        try:
            resultado = app.mover(paso.direccion)
        finally:
            self.en_paso = False
        if not resultado.ok:
            return self._detener("movimiento_rechazado",
                                 f"Viaje detenido: no se pudo avanzar ({resultado.motivo}).")
        self.pasos += 1
        if app._jugador.sala == self.destino:
            return self._detener("llegada", f"Viaje detenido: llegaste a la sala {self.destino}.", ok=True)
        return ResultadoViaje(ok=True, activo=True)

    def cancelar(self) -> ResultadoViaje:
        """Interrumpe el viaje activo con el motivo `cancelado` (FR-034)."""
        if not self.activo:
            return ResultadoViaje(ok=False, activo=False, motivo=self.motivo)
        return self._detener("cancelado", "Viaje cancelado.")
