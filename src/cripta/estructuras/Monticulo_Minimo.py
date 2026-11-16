"""Montículo mínimo genérico con listas paralelas.

Se eligió un montículo binario propio (sin `heapq`) con tres listas paralelas:
prioridad, desempate y elemento. La comparación es lexicográfica por
`(prioridad, desempate)` con enteros, así el orden es determinista sin depender
de comparar los elementos. La eliminación es perezosa: el llamador reinserta un
elemento con mejor prioridad y descarta las entradas obsoletas al extraer.
No reemplaza al heap de la agenda de eventos.

Complejidad:
    insertar: O(log n)
    extraer_minimo: O(log n)
    esta_vacio: O(1)
    vaciar: O(1), conserva la memoria reservada para otra búsqueda
"""

from __future__ import annotations

from typing import Any


class MonticuloMinimo:
    def __init__(self) -> None:
        self._prioridad: list[int] = []
        self._desempate: list[int] = []
        self._elemento: list[Any] = []
        self._tamano = 0  # posiciones vivas; las listas conservan su largo entre búsquedas

    def esta_vacio(self) -> bool:
        return self._tamano == 0

    def __len__(self) -> int:
        return self._tamano

    def vaciar(self) -> None:
        """Deja el montículo vacío sin reasignar las listas (O(1))."""
        self._tamano = 0

    def _menor(self, i: int, j: int) -> bool:
        if self._prioridad[i] != self._prioridad[j]:
            return self._prioridad[i] < self._prioridad[j]
        return self._desempate[i] < self._desempate[j]

    def _intercambiar(self, i: int, j: int) -> None:
        self._prioridad[i], self._prioridad[j] = self._prioridad[j], self._prioridad[i]
        self._desempate[i], self._desempate[j] = self._desempate[j], self._desempate[i]
        self._elemento[i], self._elemento[j] = self._elemento[j], self._elemento[i]

    def insertar(self, prioridad: int, desempate: int, elemento: Any) -> None:
        """Agrega un elemento (O(log n))."""
        posicion = self._tamano
        if posicion < len(self._prioridad):
            self._prioridad[posicion] = prioridad
            self._desempate[posicion] = desempate
            self._elemento[posicion] = elemento
        else:
            self._prioridad.append(prioridad)
            self._desempate.append(desempate)
            self._elemento.append(elemento)
        self._tamano += 1
        while posicion > 0:
            padre = (posicion - 1) // 2
            if not self._menor(posicion, padre):
                break
            self._intercambiar(posicion, padre)
            posicion = padre

    def extraer_minimo(self) -> list:
        """Quita y devuelve `[prioridad, desempate, elemento]` del menor (O(log n)).

        Es un error del llamador extraer de un montículo vacío; se consulta
        `esta_vacio` antes.
        """
        if self._tamano == 0:
            raise IndexError("Montículo vacío.")
        resultado = [self._prioridad[0], self._desempate[0], self._elemento[0]]
        self._tamano -= 1
        ultimo = self._tamano
        if ultimo > 0:
            self._prioridad[0] = self._prioridad[ultimo]
            self._desempate[0] = self._desempate[ultimo]
            self._elemento[0] = self._elemento[ultimo]
        self._elemento[ultimo] = None  # no retener referencias
        posicion = 0
        while True:
            izquierdo = 2 * posicion + 1
            if izquierdo >= self._tamano:
                break
            menor = izquierdo
            derecho = izquierdo + 1
            if derecho < self._tamano and self._menor(derecho, izquierdo):
                menor = derecho
            if not self._menor(menor, posicion):
                break
            self._intercambiar(posicion, menor)
            posicion = menor
        return resultado
