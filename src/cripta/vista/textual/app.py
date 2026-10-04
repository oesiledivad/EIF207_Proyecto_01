"""App de Textual."""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.textual.screens.cargando import CargandoScreen


_ESTILOS = Path(__file__).parent / "estilos"


class CriptaApp(App):
    """Aplicación Textual del proyecto Cripta."""

    CSS_PATH = [
        str(_ESTILOS / "base.tcss"),
        str(_ESTILOS / "seleccion.tcss"),
        str(_ESTILOS / "juego.tcss"),
        str(_ESTILOS / "mini_mapa.tcss"),
        str(_ESTILOS / "modales.tcss"),
        str(_ESTILOS / "cargando.tcss")
    ]

    TITLE = "Cripta"

    def __init__(self, controlador: Aplicacion) -> None:
        super().__init__()
        self._controlador = controlador

    def on_mount(self) -> None:
        self.push_screen(
            CargandoScreen(
                mensaje="Conectando con el servicio",
                controlador=self._controlador,
                siguiente="seleccion",
                modo="pantalla",
            )
        )