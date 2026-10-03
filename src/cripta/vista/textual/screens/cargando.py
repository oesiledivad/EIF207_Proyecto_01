from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class CargandoScreen(ModalScreen):
    """Modal con spinner ASCII."""

    # Sube a la carpeta 'textual' y entra a 'estilos/cargando.tcss'
    CSS_PATH = Path(__file__).parent.parent / "estilos" / "cargando.tcss"

    def __init__(self, mensaje: str = "Cargando") -> None:
        super().__init__()
        self._mensaje = mensaje
        self._frame = 0
        self._timer = None

    def compose(self) -> ComposeResult:
        with Vertical(id="cargando-caja"):
            yield Static("", id="cargando-texto")

    def on_mount(self) -> None:
        self._actualizar()
        self._timer = self.set_interval(0.08, self._tick)

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % len(_FRAMES)
        self._actualizar()

    def _actualizar(self) -> None:
        spinner = _FRAMES[self._frame]
        self.query_one("#cargando-texto", Static).update(
            f"[bold #e8a33d]{spinner}[/]  [bold #ffffff]{self._mensaje}...[/]"
        )

    def on_unmount(self) -> None:
        if self._timer:
            self._timer.stop()