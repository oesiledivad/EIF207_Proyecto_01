"""Las salidas de una sala (2.1): máximo N/S/E/O. Evita dict como tabla de búsqueda."""

from __future__ import annotations
from dataclasses import dataclass, field      #  CAMBIA: se agrega "field"
@dataclass
class SalidaSimple:
    direccion: str
    sala_destino: int
    cerrada: bool
    llave: str | None = None
    cierre_automatico: int | None = None
    costo: int = 100   # mayor o igual que 1; 100 si no se declara (FR-023)
    clave: int = 0     # origen * 4 + índice de dirección; la fija `ensamblar_salas` (FR-007)
    # Evento de cierre pendiente en la agenda (None si no hay). No forma parte de la identidad.   # <- NUEVO
    evento_cierre: object | None = field(default=None, repr=False, compare=False)                   # <- NUEVO


def indice_direccion(direccion: str) -> int:
    """Índice de la dirección: N 0, S 1, E 2, O 3 (comparación explícita, sin dict)."""
    if direccion == "N":
        return 0
    if direccion == "S":
        return 1
    if direccion == "E":
        return 2
    return 3


class Salidas:
    def __init__(self) -> None:
        self._lista: list[SalidaSimple] = []

    def agregar(self, direccion: str, sala_destino: int, cerrada: bool,
                llave: str | None = None, cierre_automatico: int | None = None,
                costo: int = 100) -> None:
        self._lista.append(SalidaSimple(direccion, sala_destino, cerrada, llave, cierre_automatico, costo))

    def obtener(self, direccion: str) -> SalidaSimple | None:
        for s in self._lista:
            if s.direccion == direccion:
                return s
        return None

    def __iter__(self):
        return iter(self._lista)