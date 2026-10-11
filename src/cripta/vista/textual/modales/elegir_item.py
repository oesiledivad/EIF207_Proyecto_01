"""Modal para elegir un item del inventario."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Static

from cripta.estructuras.Inventario import Inventario, ItemInventario


class ElegirItemModal(ModalScreen):
    """Devuelve el item elegido al cerrar, o None si se cancela.

    Args:
        inventario: Inventario del jugador.
        accion: Texto que describe para qué se elige (usar, equipar, soltar).
        filtro_clase: Si no es None, solo muestra items de esa clase.
    """

    BINDINGS = [("escape", "cancelar", "Cancelar")]

    def __init__(
        self,
        inventario: Inventario | list[ItemInventario],
        accion: str,
        filtro_clase: str | None = None,
    ) -> None:
        super().__init__()
        self._inventario = inventario
        self._accion = accion
        self._filtro = filtro_clase
        self._items: list[ItemInventario] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-root"):
            yield Static(f"Elegir item para {self._accion}", id="modal-titulo")
            yield DataTable(id="modal-tabla")
        yield Footer()

    def on_mount(self) -> None:
        tabla = self.query_one("#modal-tabla", DataTable)
        tabla.add_columns("Nombre", "Clase", "Peso", "Valor", "Equip.")
        tabla.cursor_type = "row"
        tabla.zebra_stripes = True
        tabla.focus()

        items = self._inventario.items() if isinstance(self._inventario, Inventario) else self._inventario
        for item in items:
            if self._filtro is not None and item.clase != self._filtro:
                continue
            self._items.append(item)
            equipo = "sí" if item.equipado else ""
            tabla.add_row(
                item.nombre,
                item.clase,
                str(item.peso),
                str(item.valor),
                equipo,
                key=item.instancia_id,
            )

        if self._items:
            tabla.move_cursor(row=0)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.dismiss(self._items[event.cursor_row])

    def action_cancelar(self) -> None:
        self.dismiss(None)
