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
        # Datos de la ficha que la instancia necesita después de creada:
        self.tipo: str | None = None              # id de catálogo (para proteger la ficha en caché)
        self.suelta: list[str] = []               # botín al morir (§2.6)
        self.regeneracion_objetivo: int | None = None  # None si no regenera (§2.10)
        self.nombre: str = identificador          # nombre de la ficha (lo pone CombateControlador)

    def decidir_accion(self, sala_jugador_id, salas: IndiceSalas, tiempo_actual: int, azar):
        if self.sala == sala_jugador_id:
            return "atacar", None
        return self._decidir_movimiento(salas, tiempo_actual, azar)

    def _decidir_movimiento(self, salas: IndiceSalas, tiempo_actual: int, azar):
        raise NotImplementedError