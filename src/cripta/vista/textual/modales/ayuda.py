"""Modal de ayuda con atajos."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


_AYUDA = """\
ATAJOS
  M  mover            A  atacar         .  esperar
  O  abrir puerta     R  recoger        U  usar
  E  equipar          S  soltar         P  pergamino
  G  guardar          C  cargar         ?  ayuda
  Q  terminar

INVENTARIO
  P  vista por peso   V  vista por valor
  N  vista por nombre R  orden real

SELECCIÓN
  Flechas  navegar    Enter  seleccionar
  Esc      salir
"""


class AyudaModal(ModalScreen):
    BINDINGS = [("escape", "cerrar", "Cerrar")]

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-root"):
            yield Static("AYUDA", id="modal-titulo")
            yield Static(_AYUDA, id="modal-cuerpo")

    def action_cerrar(self) -> None:
        self.dismiss(None)