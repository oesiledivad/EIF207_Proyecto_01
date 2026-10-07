"""Historial invertible de cambios entre acciones del jugador.

Se eligió una pila de intervalos con listas de cambios porque §2.11
prohíbe copias completas del estado. Cada intervalo agrupa los cambios
ocurridos entre dos decisiones del jugador y se puede invertir en orden
inverso.

Solo se retienen los últimos 5 intervalos; al superar el límite se
descarta el más antiguo.

Complejidad:
    abrir_intervalo: O(1)
    registrar: O(1)
    cerrar_intervalo: O(1) amortizado
    deshacer: O(k), k = cambios del intervalo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Cambio:
    """Un cambio invertible registrado en el historial.

    Attributes:
        etiqueta: Nombre del cambio (por ejemplo "vida_jugador").
        datos: Información necesaria para invertirlo.
    """

    etiqueta: str
    datos: Any


@dataclass
class Intervalo:
    """Conjunto de cambios entre dos decisiones del jugador."""

    cambios: list[Cambio] = field(default_factory=list)


class Historial_Retroceso:
    """Pila de intervalos invertibles con tope de 5.

    Args:
        max_intervalos: Número máximo de intervalos retenidos.
    """

    def __init__(self, max_intervalos: int = 5) -> None:
        if max_intervalos <= 0:
            raise ValueError("El máximo de intervalos debe ser positivo.")
        self._max = max_intervalos
        self._intervalos: list[Intervalo] = []
        self._abierto: Intervalo | None = None

    def abrir_intervalo(self) -> None:
        """Inicia un nuevo intervalo de cambios."""
        if self._abierto is not None:
            raise RuntimeError("Ya hay un intervalo abierto.")
        self._abierto = Intervalo()

    def registrar(self, etiqueta: str, datos: Any) -> None:
        """Registra un cambio invertible en el intervalo abierto.

        Args:
            etiqueta: Nombre del cambio.
            datos: Información para invertirlo.
        """
        if self._abierto is None:
            raise RuntimeError("No hay intervalo abierto.")
        self._abierto.cambios.append(Cambio(etiqueta, datos))

    def registrar_si_abierto(self, etiqueta: str, datos: Any) -> None:
        if self._abierto is not None:
            self.registrar(etiqueta, datos)

    def cambiar(self, objeto, atributo: str, valor) -> None:
        anterior = getattr(objeto, atributo)
        if anterior != valor:
            self.registrar_si_abierto("atributo", (objeto, atributo, anterior))
            setattr(objeto, atributo, valor)

    def agregar(self, lista: list, objeto) -> None:
        self.registrar_si_abierto("lista_agregada", (lista, objeto))
        lista.append(objeto)

    def quitar(self, lista: list, objeto) -> None:
        posicion = lista.index(objeto)
        self.registrar_si_abierto("lista_quitada", (lista, posicion, objeto))
        lista.pop(posicion)

    def revertir_abierto(self, aplicar) -> None:
        if self._abierto is not None:
            for cambio in reversed(self._abierto.cambios):
                aplicar(cambio.etiqueta, cambio.datos)
            self._abierto = None

    def cerrar_intervalo(self) -> None:
        """Cierra el intervalo abierto y lo apila.

        Si se supera el tope, descarta el intervalo más antiguo.
        """
        if self._abierto is None:
            return
        self._intervalos.append(self._abierto)
        self._abierto = None
        if len(self._intervalos) > self._max:
            self._intervalos.pop(0)

    def descartar_intervalo(self) -> None:
        """Descarta el intervalo abierto sin apilarlo (la acción no se ejecutó)."""
        self._abierto = None

    def hay_intervalo_abierto(self) -> bool:
        return self._abierto is not None

    def deshacer(self, aplicar: Callable[[str, Any], None]) -> bool:
        """Aplica la inversión del intervalo más reciente.

        Args:
            aplicar: Función que recibe (etiqueta, datos) y revierte el cambio.

        Returns:
            True si se invirtió un intervalo, False si no había ninguno.
        """
        if not self._intervalos:
            return False
        intervalo = self._intervalos[-1]
        for cambio in reversed(intervalo.cambios):
            aplicar(cambio.etiqueta, cambio.datos)
        self._intervalos.pop()
        return True

    def limpiar(self) -> None:
        """Descarta todos los intervalos y el abierto."""
        self._intervalos.clear()
        self._abierto = None

    def __len__(self) -> int:
        return len(self._intervalos)