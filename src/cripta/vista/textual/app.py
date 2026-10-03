"""App de Textual. Solo monta la pantalla de selección en esta entrega."""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.textual.screens.seleccion import SeleccionCriptaScreen
_ESTILOS = Path(__file__).parent / "estilos"


class CriptaApp(App):
    """Aplicación Textual del proyecto Cripta."""

    CSS_PATH = [
        str(_ESTILOS / "base.tcss"),
        str(_ESTILOS / "seleccion.tcss"),
        str(_ESTILOS / "juego.tcss"),
        str(_ESTILOS / "cargando.tcss"),
        str(_ESTILOS / "mini_mapa.tcss"),
    ]

    TITLE = "Cripta"

    def __init__(self, controlador: Aplicacion) -> None:
        super().__init__()
        self._controlador = controlador

    def on_mount(self) -> None:
        self.push_screen(SeleccionCriptaScreen(self._controlador))