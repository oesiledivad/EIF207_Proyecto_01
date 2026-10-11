from __future__ import annotations

from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Grid
from textual.message import Message
from textual.widgets import Button
from rich.markup import escape

from cripta.dto.Partida_dto import EstadoPartida


class CeldaMapa(Button):
    """Representa una celda individual dentro del Grid del minimapa."""
    direccion: str | None = None


class MiniMapa(Grid):
    """Grid 3x3 que renderiza la sala actual y sus vecinas con widgets nativos."""

    CSS_PATH = Path(__file__).parent.parent / "estilos" / "mini_mapa.tcss"

    class Mover(Message):
        def __init__(self, direccion: str):
            super().__init__()
            self.direccion = direccion

    def on_button_pressed(self, evento: Button.Pressed) -> None:
        evento.stop()
        celda = evento.button
        if not celda.disabled and celda.direccion:
            self.post_message(self.Mover(celda.direccion))

    def compose(self) -> ComposeResult:
        # Generamos las 9 celdas fijas de la matriz 3x3
        for i in range(9):
            yield CeldaMapa("", id=f"celda-{i}", disabled=True)

    def _obtener_indice_direccion(self, direccion: str) -> int | None:
        """Mapea la dirección a un índice de la matriz 3x3 sin usar dicts."""
        if direccion == "N":
            return 1
        if direccion == "O":
            return 3
        if direccion == "E":
            return 5
        if direccion == "S":
            return 7
        return None

    def actualizar(self, p: EstadoPartida) -> None:
        # Resetear todas las celdas a estado vacío
        for i in range(9):
            celda = self.query_one(f"#celda-{i}", CeldaMapa)
            celda.label = ""
            celda.disabled = True
            celda.direccion = None
            celda.remove_class("-actual", "-cerrada", "-salida", "-vacia")
            celda.add_class("-vacia")

        # 1. Configurar Sala Actual (Posición central: celda-4)
        c_actual = self.query_one("#celda-4", CeldaMapa)
        c_actual.remove_class("-vacia")
        c_actual.add_class("-actual")
        c_actual.label = f"[bold #e8a33d]* {p.sala_actual_id} *[/]\n{escape(p.sala_actual_nombre)}"

        # 2. Asignar vecinas en la matriz (N:1, O:3, E:5, S:7)
        for v in p.vecindad:
            idx = self._obtener_indice_direccion(v.direccion)
            if idx is not None:
                celda = self.query_one(f"#celda-{idx}", CeldaMapa)
                celda.remove_class("-vacia")
                celda.direccion = v.direccion
                celda.disabled = v.cerrada or not p.activa

                if v.cerrada:
                    celda.add_class("-cerrada")
                elif v.es_salida_final:
                    celda.add_class("-salida")

                marcas = []
                if v.tiene_enemigos:
                    marcas.append("[bold #e74c3c]![/]")
                if v.tiene_objetos:
                    marcas.append("[#f1c40f]o[/]")
                if v.cerrada:
                    marcas.append("[#c9a227]K[/]")
                if v.es_salida_final:
                    marcas.append("[#8b7fb8]X[/]")

                str_marcas = " ".join(marcas)
                texto_celda = f"{v.direccion}: {escape(v.nombre)}"
                if str_marcas:
                    texto_celda += f"\n{str_marcas}"

                celda.label = texto_celda
