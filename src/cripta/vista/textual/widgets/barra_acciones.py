"""Barra de acciones en dos filas.

Todos los botones de §10.2 con su atajo. Los que aún no tienen
implementación en el controlador registran un mensaje en la bitácora.
Se divide en dos filas para caber en terminales medianas.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
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


class BarraAcciones(Vertical):
    """Barra vertical con dos filas horizontales de botones."""

    def compose(self) -> ComposeResult:
        with Horizontal(classes="fila-acciones"):
            for etiqueta, btn_id in _FILA_1:
                yield Button(etiqueta, id=btn_id)
        with Horizontal(classes="fila-acciones"):
            for etiqueta, btn_id in _FILA_2:
                classes = "-danger" if btn_id == "btn-terminar" else ""
                yield Button(etiqueta, id=btn_id, classes=classes)