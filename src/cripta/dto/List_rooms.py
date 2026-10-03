from dataclasses import dataclass
from .SalaDto import Sala

@dataclass
class List_rooms:
    """Una página del esqueleto: GET /criptas/{id}/salas?pagina=n"""
    pagina: int
    total_paginas: int
    salas: list[Sala]

    def __post_init__(self):
        self.salas = [s if isinstance(s, Sala) else Sala(**s) for s in self.salas]