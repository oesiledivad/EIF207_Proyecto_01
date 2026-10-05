"""
    src/cripta/modelo/Enemigo.py
    Representa un enemigo de la partida.
"""

from cripta.modelo.Actor import Actor
from cripta.estructuras.Indice_Salas import IndiceSalas

class Enemigo(Actor):
    def __init__(
        self,
        identificador,
        vida,
        vida_max,
        ataque,
        defensa,
        velocidad,
        sala,
        tiempo_siguiente,
        comportamiento
    ):
        super().__init__(
            identificador,
            vida,
            vida_max,
            ataque,
            defensa,
            velocidad,
            sala,
            tiempo_siguiente
        )
        # esto es la caracteristica propia de enemigo, puede ser guardian, errante o rastreador
        self.comportamiento = comportamiento

    def decidir_accion(self, sala_jugador_id, salas: IndiceSalas, tiempo_actual: int, azar):
        if self.sala == sala_jugador_id:
            return "atacar", None
        return self._decidir_movimiento(salas, tiempo_actual, azar)

    def _decidir_movimiento(self, salas: IndiceSalas, tiempo_actual: int, azar):
        raise NotImplementedError