"""Enemigo cazador (spec 003, Parte II §3.2): persigue al jugador por la ruta más barata.

En su turno: ataca si comparte sala con el jugador (lo decide `Enemigo.decidir_accion`); si no,
espera si no hay ruta abierta o si el costo mínimo d supera su rango; si no, da un paso por una ruta
de costo d y esa acción cuesta lo que la salida (FR-010 a FR-014).

Conoce el esqueleto completo y el estado actual de las puertas; no lee el conocimiento del jugador y
nunca abre puertas (FR-015, FR-016). La búsqueda la hace `Persecucion`, compartida entre cazadores.
"""
from cripta.modelo.Enemigo import Enemigo


class Cazador(Enemigo):
    def __init__(self, identificador, vida, vida_max, ataque, defensa,
                 velocidad, sala, tiempo_siguiente, comportamiento="cazador", rango=0):
        super().__init__(identificador, vida, vida_max, ataque, defensa,
                          velocidad, sala, tiempo_siguiente, comportamiento)
        self.rango = rango   # en unidades de costo, >= 0 (FR-008)

    def _decidir_movimiento(self, salas, tiempo_actual, azar, persecucion=None, sala_jugador_id=None):
        if persecucion is None:
            return ["esperar", None, None]   # sin búsqueda configurada no hay ruta (FR-012)
        sala_actual = salas.obtener(self.sala)
        salida = persecucion.decidir(sala_jugador_id, self.sala, sala_actual.salidas, self.rango)
        if salida is None:
            return ["esperar", None, None]
        return ["mover", salida.sala_destino, salida.costo]
