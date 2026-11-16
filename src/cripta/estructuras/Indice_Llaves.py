"""Índice de ids de llave: arreglo ordenado y búsqueda binaria propia.

El rango de un id es su posición en el arreglo ordenado por comparación de
cadenas (lexicográfica), de modo que "menor id" equivale a "menor rango".
No usa `dict`, `set` ni `bisect`.

Complejidad:
    construcción: O(n log n) con `ordenar` del proyecto
    rango: O(log n)

Cumple: FR-008, FR-024.
"""

from __future__ import annotations

from cripta.estructuras.Ordenamientos import ordenar


class IndiceLlaves:
    """Ids de llave distintos, ordenados; el rango es la posición."""

    def __init__(self, ids: list[str]) -> None:
        # Copia para no alterar la entrada; el orden la vuelve independiente de las permutaciones.
        ordenados = ordenar(list(ids))
        distintos: list[str] = []
        for id_llave in ordenados:
            if not distintos or distintos[-1] != id_llave:
                distintos.append(id_llave)
        self._ids = distintos

    def cantidad(self) -> int:
        """Cantidad de ids distintos."""
        return len(self._ids)

    def ids(self) -> list[str]:
        """Copia de los ids en orden de rango."""
        return list(self._ids)

    def rango(self, id_llave: str) -> int:
        """Posición del id por búsqueda binaria; -1 si no existe."""
        bajo = 0
        alto = len(self._ids) - 1
        while bajo <= alto:
            medio = (bajo + alto) // 2
            actual = self._ids[medio]
            if actual == id_llave:
                return medio
            if actual < id_llave:
                bajo = medio + 1
            else:
                alto = medio - 1
        return -1
