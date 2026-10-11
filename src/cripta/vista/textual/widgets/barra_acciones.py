"""Barra de acciones con atajos y columnas adaptables a la terminal."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button


_FILA_1 = [
    ["Mover [M]", "btn-mover"],
    ["Atacar [A]", "btn-atacar"],
    ["Esperar [.]", "btn-esperar"],
    ["Abrir [O]", "btn-abrir"],
    ["Recoger [R]", "btn-recoger"],
]

_FILA_2 = [
    ["Usar [U]", "btn-usar"],
    ["Equipar [E]", "btn-equipar"],
    ["Soltar [S]", "btn-soltar"],
    ["Pergamino [P]", "btn-pergamino"],
    ["Guardar [G]", "btn-guardar"],
    ["Cargar [C]", "btn-cargar"],
    ["Ayuda [?]", "btn-ayuda"],
    ["Terminar [Q]", "btn-terminar"],
]


class BarraAcciones(Grid):
    """Acciones en una cuadrícula adaptable al ancho de la terminal."""

    def compose(self) -> ComposeResult:
        for etiqueta, btn_id in _FILA_1 + _FILA_2:
            classes = "-danger" if btn_id == "btn-terminar" else ""
            yield Button(etiqueta, id=btn_id, classes=classes)
