"""
    src/cripta/util/Reloj.py
    Maneja el tiempo virtual de la simulación.
"""


class Reloj:
    def __init__(self, historial=None):
        self.tiempo_actual = 0
        self._historial = historial

    def avanzar_hasta(self, nuevo_tiempo: int) -> None:
        if nuevo_tiempo < self.tiempo_actual:
            raise ValueError("El reloj no puede retroceder")

        if self._historial is None:
            self.tiempo_actual = nuevo_tiempo
        else:
            self._historial.cambiar(self, "tiempo_actual", nuevo_tiempo)