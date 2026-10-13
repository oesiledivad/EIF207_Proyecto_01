from __future__ import annotations

import struct


class EscritorBinario:
    """Acumula campos en una lista de trozos de bytes y los une al final."""

    def __init__(self) -> None:
        self._partes: list[bytes] = []

    def entero(self, valor: int) -> None:
        self._partes.append(struct.pack(">q", valor))

    def sin_signo(self, valor: int) -> None:
        self._partes.append(struct.pack(">I", valor))

    def booleano(self, valor: bool) -> None:
        self._partes.append(struct.pack(">B", 1 if valor else 0))

    def decimal(self, valor: float) -> None:
        self._partes.append(struct.pack(">d", valor))

    def texto(self, valor: str) -> None:
        crudo = valor.encode("utf-8")
        self._partes.append(struct.pack(">I", len(crudo)))
        self._partes.append(crudo)

    def entero_opcional(self, valor: int | None) -> None:
        self.booleano(valor is not None)
        if valor is not None:
            self.entero(valor)

    def texto_opcional(self, valor: str | None) -> None:
        self.booleano(valor is not None)
        if valor is not None:
            self.texto(valor)

    def decimal_opcional(self, valor: float | None) -> None:
        self.booleano(valor is not None)
        if valor is not None:
            self.decimal(valor)

    def a_bytes(self) -> bytes:
        return b"".join(self._partes)
