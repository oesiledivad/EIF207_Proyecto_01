"""Cola FIFO propia sobre una lista con índice de cabeza.

No usa `collections.deque` ni `list.pop(0)`: sacar un elemento solo avanza el
índice de cabeza, así que encolar y sacar son O(1) amortizado.

Cumple: FR-024.
"""

from __future__ import annotations
from typing import Any


class ColaLista:
    """Cola FIFO con `list` y un índice de cabeza."""

    def __init__(self) -> None:
        self._datos: list[Any] = []
        self._cabeza = 0

    def encolar(self, valor: Any) -> None:
        """Agrega un elemento al final. O(1) amortizado."""
        self._datos.append(valor)

    def sacar(self) -> Any:
        """Quita y devuelve el elemento más antiguo. O(1).

        Raises:
            IndexError: si la cola está vacía.
        """
        if self._cabeza >= len(self._datos):
            raise IndexError("sacar de una cola vacía")
        valor = self._datos[self._cabeza]
        self._datos[self._cabeza] = None   # suelta la referencia sin desplazar la lista
        self._cabeza += 1
        return valor

    def vacia(self) -> bool:
        """Indica si no quedan elementos."""
        return self._cabeza >= len(self._datos)
