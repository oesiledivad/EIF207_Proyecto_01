"""
    src/cripta/util/Reloj.py
    Maneja el tiempo virtual de la simulación.
"""


class Reloj:
    def __init__(self):
        self.tiempo_actual = 0

    def avanzar_hasta(self, nuevo_tiempo: int) -> None:
        if nuevo_tiempo < self.tiempo_actual:
            raise ValueError("El reloj no puede retroceder")

        self.tiempo_actual = nuevo_tiempo