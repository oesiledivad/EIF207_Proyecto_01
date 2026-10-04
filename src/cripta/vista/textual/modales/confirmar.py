"""Modal de confirmación sí/no."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmarModal(ModalScreen):
    """Devuelve True si el usuario confirma, False si cancela.

    Args:
        mensaje: Texto a mostrar.
    """

    BINDINGS = [
        ("escape", "cancelar", "Cancelar"),
        ("enter", "confirmar", "Confirmar"),
    ]

    def __init__(self, mensaje: str) -> None:
        super().__init__()
        self._mensaje = mensaje

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-root"):
            yield Static(self._mensaje, id="modal-titulo")
            with Horizontal(id="modal-acciones"):
                yield Button("Confirmar", id="btn-si", classes="-primary")
                yield Button("Cancelar", id="btn-no", classes="-danger")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-si":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirmar(self) -> None:
        self.dismiss(True)

    def action_cancelar(self) -> None:
        self.dismiss(False)