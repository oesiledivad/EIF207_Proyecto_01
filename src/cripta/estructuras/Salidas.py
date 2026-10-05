"""Las salidas de una sala (§2.1): máximo N/S/E/O. Evita dict como tabla de búsqueda."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SalidaSimple:
    direccion: str
    sala_destino: int
    cerrada: bool


class Salidas:
    def __init__(self) -> None:
        self._lista: list[SalidaSimple] = []

    def agregar(self, direccion: str, sala_destino: int, cerrada: bool) -> None:
        self._lista.append(SalidaSimple(direccion, sala_destino, cerrada))

    def obtener(self, direccion: str) -> SalidaSimple | None:
        for s in self._lista:
            if s.direccion == direccion:
                return s
        return None

    def __iter__(self):
        return iter(self._lista)