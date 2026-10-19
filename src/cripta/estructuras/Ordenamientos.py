"""Algoritmos de ordenamiento propios con selección automática.

Se implementaron insertion sort y merge sort porque 4.9 exige al menos
dos algoritmos con características distintas y elección automática según
propiedades medibles. Insertion sort es O(n) en datos casi ordenados;
merge sort garantiza O(n log n) y es estable.

No se usa `sorted` ni `list.sort`.

Complejidad:
    insertion_sort: O(n^2) peor, O(n) si casi ordenado
    merge_sort: O(n log n) siempre
    ordenar: elige según n y grado de orden medido
"""

from __future__ import annotations

from typing import Any, Callable


Key = Callable[[Any], Any] | None


def insertion_sort(lista: list, key: Key = None) -> list:
    """Ordena con insertion sort, estable.

    Args:
        lista: Lista a ordenar (se modifica in place).
        key: Función que extrae la clave de comparación. Si es None,
            se compara el elemento directamente.

    Returns:
        La misma lista ordenada.
    """
    f = key if key is not None else (lambda x: x)
    for i in range(1, len(lista)):
        actual = lista[i]
        clave_actual = f(actual)
        j = i - 1
        while j >= 0 and f(lista[j]) > clave_actual:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = actual
    return lista


def merge_sort(lista: list, key: Key = None) -> list:
    """Ordena con merge sort, estable.

    Args:
        lista: Lista a ordenar (se modifica in place).
        key: Función que extrae la clave de comparación. Si es None,
            se compara el elemento directamente.

    Returns:
        La misma lista ordenada.
    """
    f = key if key is not None else (lambda x: x)

    def _merge(a: list, b: list) -> list:
        resultado = []
        i = j = 0
        while i < len(a) and j < len(b):
            if f(a[i]) <= f(b[j]):
                resultado.append(a[i])
                i += 1
            else:
                resultado.append(b[j])
                j += 1
        resultado.extend(a[i:])
        resultado.extend(b[j:])
        return resultado

    def _sort(arr: list) -> list:
        if len(arr) <= 1:
            return arr
        medio = len(arr) // 2
        izq = _sort(arr[:medio])
        der = _sort(arr[medio:])
        return _merge(izq, der)

    ordenada = _sort(lista)
    lista[:] = ordenada
    return lista


def _casi_ordenado(lista: list, key: Key, muestra: int = 64) -> bool:
    """Heurística: cuenta inversiones en una muestra pequeña."""
    f = key if key is not None else (lambda x: x)
    n = len(lista)
    if n <= 1:
        return True
    paso = max(1, n // muestra)
    inversiones = 0
    comparaciones = 0
    for i in range(0, n - paso, paso):
        comparaciones += 1
        if f(lista[i]) > f(lista[i + paso]):
            inversiones += 1
    return comparaciones > 0 and inversiones / comparaciones < 0.1


def ordenar(lista: list, key: Key = None) -> list:
    """Elige el algoritmo según n y grado de orden.

    Args:
        lista: Lista a ordenar (se modifica in place).
        key: Función que extrae la clave de comparación.

    Returns:
        La misma lista ordenada.
    """
    n = len(lista)
    if n <= 16:
        return insertion_sort(lista, key)
    if _casi_ordenado(lista, key):
        return insertion_sort(lista, key)
    return merge_sort(lista, key)