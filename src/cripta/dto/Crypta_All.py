

from dataclasses import dataclass

@dataclass
class Crypta_all:
    """Una cripta de la lista devuelta por GET /criptas"""
    id: str
    nombre: str
    salas: int
    dificultad: int