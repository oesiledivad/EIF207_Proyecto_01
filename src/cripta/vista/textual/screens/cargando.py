"""Pantalla de carga con spinner ASCII.

Se usa de dos formas:
- Modo pantalla: se monta como pantalla completa y, si recibe un
  controlador y un destino, encadena a otra pantalla al terminar.
- Modo modal: se pushea encima de la pantalla activa y espera a que el
  llamador haga pop_screen.

El spinner es ASCII puro y los colores siguen la paleta "Cripta".
"""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


_FRAMES = ["|", "/", "-", "\\"]

class CargandoScreen(ModalScreen):
    """Pantalla con spinner ASCII.
    Args:
        mensaje: Texto a mostrar junto al spinner.
        controlador: Si se pasa, se usa para precargar datos.
        siguiente: Nombre de la pantalla destino (solo modo pantalla).
        modo: "pantalla" o "modal".
    """
    def __init__(
        self,
        mensaje: str = "Cargando",
        controlador=None,
        siguiente: str | None = None,
        modo: str = "modal",
    ) -> None:
        super().__init__()
        self._mensaje = mensaje
        self._controlador = controlador
        self._siguiente = siguiente
        self._modo = modo
        self._frame = 0
        self._timer = None
    def compose(self) -> ComposeResult:
        with Vertical(id="cargando-caja"):
            yield Static("", id="cargando-texto")
    def on_mount(self) -> None:
        # Modo pantalla ocupa todo el ancho; modo modal queda centrado.
        if self._modo == "pantalla":
            self.add_class("-pantalla")
        else:
            self.add_class("-modal")

        self._actualizar()
        self._timer = self.set_interval(0.1, self._tick)

        if self._controlador is not None and self._siguiente is not None:
            self._precargar()

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % len(_FRAMES)
        self._actualizar()

    def _actualizar(self) -> None:
        spinner = _FRAMES[self._frame]
        self.query_one("#cargando-texto", Static).update(
            f"[bold #e8a33d]{spinner}[/]  [#d6cfc4]{self._mensaje}...[/]"
        )
    def _precargar(self) -> None:
        """Ejecuta la precarga en un worker y encadena según `siguiente`."""

        def _trabajo() -> None:
            try:
                criptas = self._controlador.listar_criptas()
                error = ""
            except Exception as e:
                criptas = []
                error = str(e)
            self.app.call_from_thread(self._al_terminar, criptas, error)

        self.run_worker(_trabajo, thread=True)

    def _al_terminar(self, criptas, error: str) -> None:
        if self._timer:
            self._timer.stop()

        if self._siguiente == "seleccion":
            from cripta.vista.textual.screens.seleccion import (
                SeleccionCriptaScreen,
            )
            self.app.switch_screen(
                SeleccionCriptaScreen(
                    self._controlador, criptas=criptas, error=error
                )
            )
        # Otros destinos se añaden cuando haga falta.

    def on_unmount(self) -> None:
        if self._timer:
            self._timer.stop()