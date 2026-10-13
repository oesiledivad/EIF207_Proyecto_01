from __future__ import annotations

import struct



class LectorBinario:
    """Lee los campos en el mismo orden en que se escribieron."""

    def __init__(self, datos: bytes) -> None:
        self._datos = datos
        self._posicion = 0

    def _tomar(self, cantidad: int) -> bytes:
        fin = self._posicion + cantidad
        if cantidad < 0 or fin > len(self._datos):
            raise ValueError("Guardado dañado: faltan datos.")
        trozo = self._datos[self._posicion:fin]
        self._posicion = fin
        return trozo

    def entero(self) -> int:
        return struct.unpack(">q", self._tomar(8))[0]

    def sin_signo(self) -> int:
        return struct.unpack(">I", self._tomar(4))[0]

    def booleano(self) -> bool:
        return struct.unpack(">B", self._tomar(1))[0] == 1

    def decimal(self) -> float:
        return struct.unpack(">d", self._tomar(8))[0]

    def texto(self) -> str:
        longitud = struct.unpack(">I", self._tomar(4))[0]
        return self._tomar(longitud).decode("utf-8")

    def entero_opcional(self) -> int | None:
        return self.entero() if self.booleano() else None

    def texto_opcional(self) -> str | None:
        return self.texto() if self.booleano() else None

    def decimal_opcional(self) -> float | None:
        return self.decimal() if self.booleano() else None

    def al_final(self) -> bool:
        return self._posicion == len(self._datos)