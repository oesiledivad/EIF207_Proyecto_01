"""
    src/cripta/modelo/Jugador.py
    Representa al jugador de la partida.
    Hereda de Actor.
"""

from cripta.modelo.Actor import Actor

class Jugador(Actor):
    def __init__(self,
        identificador,
        vida,
        vida_max,
        ataque,
        defensa,
        velocidad,
        sala,
        tiempo_siguiente,
        inventario_max
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
        # Estos le pertenecen al jugador y no a los enemigos, por eso se definen aquí.
        self.inventario_max = inventario_max

