"""Bitácora de juego con buffer circular de tamaño fijo.

Se eligió un buffer circular sobre `list` con índice de escritura porque
§4.8 exige memoria constante y que agregar no desplace físicamente los
mensajes anteriores. Una `list` con `pop(0)` sería O(n) por mensaje.

Complejidad:
    append: O(1)
    ultimos: O(k), k = tamaño del buffer
    memoria: O(k) constante
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Mensaje:
    """Un mensaje de la bitácora.

    Attributes:
        tipo: Categoría del mensaje (sistema, jugador, enemigo, efecto).
        texto: Contenido legible del mensaje.
    """

    tipo: str
    texto: str


class Bitacora:
    """Buffer circular de mensajes con capacidad fija.

    Args:
        capacidad: Número máximo de mensajes retenidos. Por defecto 20.
    """

    def __init__(self, capacidad: int = 20) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")
        self._capacidad = capacidad
        self._buffer: list[Mensaje | None] = [None] * capacidad
        self._inicio = 0
        self._tamano = 0

    def append(self, mensaje: Mensaje) -> None:
        """Agrega un mensaje, sobreescribiendo el más antiguo si está lleno.

        Args:
            mensaje: Mensaje a registrar.
        """
        if self._tamano < self._capacidad:
            idx = (self._inicio + self._tamano) % self._capacidad
            self._buffer[idx] = mensaje
            self._tamano += 1
        else:
            self._buffer[self._inicio] = mensaje
            self._inicio = (self._inicio + 1) % self._capacidad

    def ultimos(self) -> list[Mensaje | None]:
        """Devuelve los mensajes en orden cronológico.

        Returns:
            Lista con los mensajes actuales, del más antiguo al más reciente.
        """
        return [
            self._buffer[(self._inicio + i) % self._capacidad]
            for i in range(self._tamano)
        ]

    def limpiar(self) -> None:
        """Descarta todos los mensajes."""
        self._buffer = [None] * self._capacidad
        self._inicio = 0
        self._tamano = 0

    def __len__(self) -> int:
        return self._tamano