"""Modal para elegir un enemigo de la sala."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Static

from cripta.dto.Partida_dto import EnemigoPartida


class ElegirEnemigoModal(ModalScreen):
    """Permite seleccionar un enemigo para atacar."""

    BINDINGS = [("escape", "cancelar", "Cancelar")]

    def __init__(self, enemigos: list[EnemigoPartida]) -> None:
        super().__init__()
        self._enemigos = enemigos

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-root"):
            yield Static("Elegir enemigo para atacar", id="modal-titulo")
            yield DataTable(id="modal-tabla")
        yield Footer()

    def on_mount(self) -> None:
        tabla = self.query_one("#modal-tabla", DataTable)
        tabla.add_columns("Enemigo", "Vida")
        tabla.cursor_type = "row"
        tabla.zebra_stripes = True

        for enemigo in self._enemigos:
            tabla.add_row(enemigo.nombre, f"{enemigo.vida}/{enemigo.vida_max}", key=enemigo.id)

        if self._enemigos:
            tabla.move_cursor(row=0)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.dismiss(self._enemigos[event.cursor_row])

    def action_cancelar(self) -> None:
        self.dismiss(None)