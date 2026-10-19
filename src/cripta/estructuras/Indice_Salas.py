"""Índice de salas ya ensambladas, por id (4.2).

Direccionamiento directo con list: los ids de sala son enteros pequeños
y secuenciales por cripta, así que list[id] es O(1) real sin necesidad
de tabla hash. 7 permite list como almacenamiento contiguo de bajo nivel.
"""

from __future__ import annotations
from typing import Any


class IndiceSalas:
    def __init__(self, capacidad_inicial: int = 64) -> None:
        self._datos: list[Any | None] = [None] * capacidad_inicial

    def _asegurar_capacidad(self, clave: int) -> None:
        if clave >= len(self._datos):
            crecimiento = max(clave + 1, len(self._datos) * 2)
            self._datos.extend([None] * (crecimiento - len(self._datos)))

    def obtener(self, clave: int) -> Any | None:
        if clave < 0 or clave >= len(self._datos):
            return None
        return self._datos[clave]

    def contiene(self, clave: int) -> bool:
        return self.obtener(clave) is not None

    def insertar(self, clave: int, valor: Any) -> None:
        self._asegurar_capacidad(clave)
        self._datos[clave] = valor