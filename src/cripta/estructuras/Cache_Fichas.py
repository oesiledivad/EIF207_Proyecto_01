"""Cache de fichas con lista doble enlazada propia y desalojo LRU.

La misma lista sirve para buscar por clave y mantener la recencia.
Las fichas con referencias activas nunca se desalojan. Si todas estan
protegidas, insertar una ficha nueva falla sin superar la capacidad.

Buscar, insertar, obtener, marcar y liberar cuestan O(n), donde n esta
limitado por --cache-size. Mover o desenlazar un nodo conocido cuesta O(1).
El desalojo busca desde la cola la ficha libre menos reciente: O(n).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class _Nodo:
    """Nodo de la lista doble enlazada LRU."""

    clave: str
    ficha: Any
    referencias: int = 0
    anterior_lru: "_Nodo | None" = None
    siguiente_lru: "_Nodo | None" = None


class Cache_Fichas:
    """Caché LRU de fichas con tope configurable.

    Args:
        capacidad: Número máximo de fichas en memoria.
    """

    def __init__(self, capacidad: int = 25) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")
        self._capacidad = capacidad
        self._cabeza_lru: _Nodo | None = None
        self._cola_lru: _Nodo | None = None
        self._tamano = 0
        self._en_uso = 0
        self._aciertos = 0
        self._fallos = 0
        self._desalojos = 0

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

    def marcar_en_uso(self, clave: str) -> bool:
        """Suma una referencia a la ficha (deja de ser desalojable).

        Args:
            clave: Identificador de la ficha.

        Returns:
            True si la ficha estaba en memoria; False si no (hay que traerla).
        """
        nodo = self._buscar(clave)
        if nodo is None:
            return False
        if nodo.referencias == 0:
            self._en_uso += 1
        nodo.referencias += 1
        return True

    def liberar(self, clave: str) -> None:
        """Resta una referencia. Con 0 referencias vuelve a ser desalojable.

        Args:
            clave: Identificador de la ficha.
        """
        nodo = self._buscar(clave)
        if nodo is not None and nodo.referencias > 0:
            nodo.referencias -= 1
            if nodo.referencias == 0:
                self._en_uso -= 1

    def esta_en_uso(self, clave: str) -> bool:
        nodo = self._buscar(clave)
        return nodo is not None and nodo.referencias > 0

    def contiene(self, clave: str) -> bool:
        """Indica si la clave está en caché sin alterar LRU."""
        return self._buscar(clave) is not None

    # ---------- Internos ----------

    def _buscar(self, clave: str) -> _Nodo | None:
        nodo = self._cabeza_lru
        while nodo is not None:
            if nodo.clave == clave:
                return nodo
            nodo = nodo.siguiente_lru
        return None

    def _insertar_nuevo(self, clave: str, ficha: Any) -> None:
        self._agregar_al_frente_lru(_Nodo(clave=clave, ficha=ficha))
        self._tamano += 1

    def _desalojar_uno(self) -> None:
        nodo = self._cola_lru
        while nodo is not None and nodo.referencias > 0:
            nodo = nodo.anterior_lru
        if nodo is None:
            raise RuntimeError("Cache llena: todas las fichas estan en uso.")
        self._quitar_de_lru(nodo)
        self._tamano -= 1
        self._desalojos += 1

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

    @property
    def desalojos(self) -> int:
        return self._desalojos

    @property
    def capacidad(self) -> int:
        return self._capacidad