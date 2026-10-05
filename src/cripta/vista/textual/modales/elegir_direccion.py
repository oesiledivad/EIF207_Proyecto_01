"""Modal para elegir dirección de movimiento."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Static


class ElegirDireccionModal(ModalScreen):
    """Permite seleccionar una salida transitable para moverse."""

    BINDINGS = [("escape", "cancelar", "Cancelar")]

    def __init__(self, salidas: list) -> None:
        super().__init__()
        self._salidas = salidas  # lista de SalidaVecina, ya filtrada (sin cerradas)

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-root"):
            yield Static("Elegir dirección", id="modal-titulo")
            yield DataTable(id="modal-tabla")
        yield Footer()

    def on_mount(self) -> None:
        tabla = self.query_one("#modal-tabla", DataTable)
        tabla.add_columns("Dirección", "Sala destino")
        tabla.cursor_type = "row"
        tabla.zebra_stripes = True

        for s in self._salidas:
            tabla.add_row(s.direccion, s.nombre, key=s.direccion)

        if self._salidas:
            tabla.move_cursor(row=0)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.dismiss(self._salidas[event.cursor_row].direccion)

    def action_cancelar(self) -> None:
        self.dismiss(None)