"""Caché de fichas de catálogo con tope y desalojo LRU.

Se eligió tabla hash propia con encadenamiento más lista doble enlazada
porque §7 prohíbe `dict` como caché y §12 anticipa muchas más búsquedas
que inserciones. La lista doble mantiene el orden de recencia para el
desalojo LRU en O(1).

Las fichas en uso no se desalojan (§4.4): la política solo opera sobre
nodos con `en_uso = False`.

Complejidad (promedio, con factor de carga controlado):
    obtener: O(1)
    insertar: O(1)
    marcar_en_uso: O(1)
    liberar: O(1)
    desalojar: O(1) amortizado
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _hash_propia(clave: str, capacidad: int) -> int:
    """Hash FNV-1a de 32 bits sobre una cadena.

    Args:
        clave: Cadena a hashear.
        capacidad: Tamaño del array de buckets.

    Returns:
        Índice de bucket en [0, capacidad).
    """
    h = 2166136261
    for ch in clave:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h % capacidad


@dataclass
class _Nodo:
    """Nodo de la caché: entrada hash + enlace LRU."""

    clave: str
    ficha: Any
    en_uso: bool
    siguiente_hash: "_Nodo | None" = None
    anterior_lru: "_Nodo | None" = None
    siguiente_lru: "_Nodo | None" = None


class Cache_Fichas:
    """Caché LRU de fichas con tope configurable.

    Args:
        capacidad: Número máximo de fichas en memoria.
    """

    _CAPACIDAD_INICIAL_BUCKETS = 16
    _FACTOR_CARGA_MAX = 0.75

    def __init__(self, capacidad: int = 25) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")
        self._capacidad = capacidad
        self._n_buckets = self._CAPACIDAD_INICIAL_BUCKETS
        self._buckets: list[_Nodo | None] = [None] * self._n_buckets
        self._cabeza_lru: _Nodo | None = None
        self._cola_lru: _Nodo | None = None
        self._tamano = 0
        self._en_uso = 0
        self._aciertos = 0
        self._fallos = 0

    # ---------- API pública ----------

    def obtener(self, clave: str) -> Any | None:
        """Busca una ficha por clave y la mueve al frente de LRU.

        Args:
            clave: Identificador de la ficha.

        Returns:
            La ficha si existe, o None.
        """
        nodo = self._buscar(clave)
        if nodo is None:
            self._fallos += 1
            return None
        self._aciertos += 1
        self._mover_al_frente(nodo)
        return nodo.ficha

    def insertar(self, clave: str, ficha: Any) -> None:
        """Inserta o reemplaza una ficha.

        Args:
            clave: Identificador de la ficha.
            ficha: Objeto a almacenar.
        """
        nodo = self._buscar(clave)
        if nodo is not None:
            nodo.ficha = ficha
            self._mover_al_frente(nodo)
            return

        if self._tamano >= self._capacidad:
            self._desalojar_uno()

        self._insertar_nuevo(clave, ficha)

    def marcar_en_uso(self, clave: str) -> None:
        """Marca una ficha como en uso (no desalojable).

        Args:
            clave: Identificador de la ficha.
        """
        nodo = self._buscar(clave)
        if nodo is not None and not nodo.en_uso:
            nodo.en_uso = True
            self._en_uso += 1

    def liberar(self, clave: str) -> None:
        """Quita la marca de uso de una ficha.

        Args:
            clave: Identificador de la ficha.
        """
        nodo = self._buscar(clave)
        if nodo is not None and nodo.en_uso:
            nodo.en_uso = False
            self._en_uso -= 1

    def contiene(self, clave: str) -> bool:
        """Indica si la clave está en caché sin alterar LRU."""
        return self._buscar(clave) is not None

    # ---------- Internos ----------

    def _buscar(self, clave: str) -> _Nodo | None:
        idx = _hash_propia(clave, self._n_buckets)
        nodo = self._buckets[idx]
        while nodo is not None:
            if nodo.clave == clave:
                return nodo
            nodo = nodo.siguiente_hash
        return None

    def _insertar_nuevo(self, clave: str, ficha: Any) -> None:
        idx = _hash_propia(clave, self._n_buckets)
        nodo = _Nodo(clave=clave, ficha=ficha, en_uso=False)
        nodo.siguiente_hash = self._buckets[idx]
        self._buckets[idx] = nodo
        self._agregar_al_frente_lru(nodo)
        self._tamano += 1

        if self._tamano / self._n_buckets > self._FACTOR_CARGA_MAX:
            self._rehash()

    def _rehash(self) -> None:
        nueva_n = self._n_buckets * 2
        nuevos_buckets: list[_Nodo | None] = [None] * nueva_n

        nodo = self._cabeza_lru
        while nodo is not None:
            sig = nodo.siguiente_lru
            idx = _hash_propia(nodo.clave, nueva_n)
            nodo.siguiente_hash = nuevos_buckets[idx]
            nuevos_buckets[idx] = nodo
            nodo = sig

        self._buckets = nuevos_buckets
        self._n_buckets = nueva_n

    def _desalojar_uno(self) -> None:
        nodo = self._cola_lru
        while nodo is not None and nodo.en_uso:
            nodo = nodo.anterior_lru
        if nodo is None:
            return  # todas en uso: no se puede desalojar
        self._quitar(clave=nodo.clave, nodo=nodo)

    def _quitar(self, clave: str, nodo: _Nodo) -> None:
        idx = _hash_propia(clave, self._n_buckets)
        actual = self._buckets[idx]
        previo: _Nodo | None = None
        while actual is not None and actual is not nodo:
            previo = actual
            actual = actual.siguiente_hash
        if actual is None:
            return
        if previo is None:
            self._buckets[idx] = actual.siguiente_hash
        else:
            previo.siguiente_hash = actual.siguiente_hash
        self._quitar_de_lru(nodo)
        self._tamano -= 1

    def _agregar_al_frente_lru(self, nodo: _Nodo) -> None:
        nodo.anterior_lru = None
        nodo.siguiente_lru = self._cabeza_lru
        if self._cabeza_lru is not None:
            self._cabeza_lru.anterior_lru = nodo
        self._cabeza_lru = nodo
        if self._cola_lru is None:
            self._cola_lru = nodo

    def _quitar_de_lru(self, nodo: _Nodo) -> None:
        if nodo.anterior_lru is not None:
            nodo.anterior_lru.siguiente_lru = nodo.siguiente_lru
        else:
            self._cabeza_lru = nodo.siguiente_lru
        if nodo.siguiente_lru is not None:
            nodo.siguiente_lru.anterior_lru = nodo.anterior_lru
        else:
            self._cola_lru = nodo.anterior_lru

    def _mover_al_frente(self, nodo: _Nodo) -> None:
        if nodo is self._cabeza_lru:
            return
        self._quitar_de_lru(nodo)
        self._agregar_al_frente_lru(nodo)

    # ---------- Diagnóstico ----------

    @property
    def tamano(self) -> int:
        return self._tamano

    @property
    def aciertos(self) -> int:
        return self._aciertos

    @property
    def fallos(self) -> int:
        return self._fallos