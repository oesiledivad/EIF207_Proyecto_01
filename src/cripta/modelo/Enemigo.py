"""
    src/cripta/modelo/Enemigo.py
    Representa un enemigo de la partida.
"""

from cripta.modelo.Actor import Actor


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