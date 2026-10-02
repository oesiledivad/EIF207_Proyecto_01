from dataclasses import dataclass
from .jugadorDto import Jugador

@dataclass
class Crypta_Details:
    id: str
    version: str
    salas_total: int
    paginas: int
    sala_inicial: int
    sala_salida: int
    llave_salida: str
    presupuesto_solicitudes: int
    inventario_max: int
    jugador: Jugador

    def __post_init__(self):
        if isinstance(self.jugador, dict):
            self.jugador = Jugador(**self.jugador)