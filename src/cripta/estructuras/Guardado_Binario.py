"""Guardado binario con índice por sala.

Se eligió un formato con header + índice + cuerpo de bytes opacos porque
§4.10 exige recuperar una sala sin leer el archivo completo. El índice
guarda offsets, así que la carga selectiva no recorre el cuerpo.

El cuerpo se almacena como bytes ya serializados por el llamador: esta
estructura no conoce el modelo.

Complejidad:
    guardar: O(n), n = número de salas
    cargar_sala: O(n) la primera vez (leer índice), O(1) después
    cargar_todo: O(n)
"""

from __future__ import annotations

import struct
from dataclasses import dataclass


_MAGIC = b"CRPT"
_VERSION_FORMATO = 1

# Header: magic(4s) + version_formato(I) + longitud_version_cripta(I) +
#         n_salas(I) + offset_cuerpo(I)
_HEADER_FMT = ">4sIIII"
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)

# Índice por sala: sala_id(I) + offset(I) + longitud(I)
_ENTRADA_FMT = ">III"
_ENTRADA_SIZE = struct.calcsize(_ENTRADA_FMT)


@dataclass
class EntradaIndice:
    """Entrada del índice de salas.

    Attributes:
        sala_id: Identificador de la sala.
        offset: Posición del cuerpo de la sala en el archivo.
        longitud: Número de bytes del cuerpo.
    """

    sala_id: int
    offset: int
    longitud: int


class Guardado_Binario:
    """Serializa y recupera salas desde un archivo binario propio.

    Args:
        ruta: Ruta del archivo de guardado.
    """

    def __init__(self, ruta: str) -> None:
        self._ruta = ruta

    def guardar(
        self,
        version_cripta: str,
        salas: list[tuple[int, bytes]] | list,
    ) -> None:
        """Escribe el archivo con las salas dadas.

        Args:
            version_cripta: Versión de la cripta para detectar incompatibilidad.
            salas: Lista de objetos con atributos `sala_id` y `bytes_`.
        """
        version_bytes = version_cripta.encode("utf-8")
        n = len(salas)

        # Reservamos espacio del header + índice y calculamos offsets.
        offset_cuerpo_inicial = _HEADER_SIZE + n * _ENTRADA_SIZE
        entradas: list[EntradaIndice] = []
        offset = offset_cuerpo_inicial
        for s in salas:
            entradas.append(EntradaIndice(s.sala_id, offset, len(s.bytes_)))
            offset += len(s.bytes_)

        with open(self._ruta, "wb") as f:
            header = struct.pack(
                _HEADER_FMT,
                _MAGIC,
                _VERSION_FORMATO,
                len(version_bytes),
                n,
                offset_cuerpo_inicial,
            )
            f.write(header)
            f.write(version_bytes)

            for e in entradas:
                f.write(struct.pack(_ENTRADA_FMT, e.sala_id, e.offset, e.longitud))

            for s in salas:
                f.write(s.bytes_)

    def _leer_cabecera(self) -> tuple[str, list[EntradaIndice]]:
        with open(self._ruta, "rb") as f:
            header = f.read(_HEADER_SIZE)
            magic, version_formato, len_version, n, _ = struct.unpack(
                _HEADER_FMT, header
            )
            if magic != _MAGIC:
                raise ValueError("Archivo no es un guardado de Cripta.")
            if version_formato != _VERSION_FORMATO:
                raise ValueError(
                    f"Versión de formato incompatible: {version_formato}."
                )

            version_cripta = f.read(len_version).decode("utf-8")

            entradas: list[EntradaIndice] = []
            for _ in range(n):
                sid, off, lon = struct.unpack(_ENTRADA_FMT, f.read(_ENTRADA_SIZE))
                entradas.append(EntradaIndice(sid, off, lon))

        return version_cripta, entradas

    def cargar_sala(self, sala_id: int) -> bytes | None:
        """Recupera los bytes de una sala concreta.

        Args:
            sala_id: Identificador de la sala.

        Returns:
            Bytes de la sala, o None si no existe.
        """
        _, entradas = self._leer_cabecera()
        for e in entradas:
            if e.sala_id == sala_id:
                with open(self._ruta, "rb") as f:
                    f.seek(e.offset)
                    return f.read(e.longitud)
        return None

    def cargar_todo(self) -> list:
        """Recupera todas las salas.

        Returns:
            Lista de entradas con atributos `sala_id` y `bytes_`.
        """
        from dataclasses import dataclass as _dc

        @_dc
        class _SalaBytes:
            sala_id: int
            bytes_: bytes

        _, entradas = self._leer_cabecera()
        salas = []
        with open(self._ruta, "rb") as f:
            for e in entradas:
                f.seek(e.offset)
                salas.append(_SalaBytes(e.sala_id, f.read(e.longitud)))
        return salas

    def version_cripta(self) -> str:
        """Devuelve la versión de cripta almacenada."""
        version, _ = self._leer_cabecera()
        return version