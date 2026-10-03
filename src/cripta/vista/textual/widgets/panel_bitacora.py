"""Panel de bitácora (lee estructuras/Bitacora)."""

from __future__ import annotations

from textual.widgets import Static

from cripta.estructuras.Bitacora import Bitacora

_COLORES = {
    "sistema": "#8a7f72",
    "jugador": "#d6cfc4",
    "enemigo": "#a83a3a",
    "cura": "#7fa88a",
    "efecto": "#8b7fb8",
    "evento": "#e8a33d",
}


class PanelBitacora(Static):
    def actualizar(self, bitacora: Bitacora) -> None:
        lineas = []
        for m in bitacora.ultimos():
            color = _COLORES.get(m.tipo, "#d6cfc4")
            lineas.append(f"[{color}]> {m.texto}[/]")
        self.update("\n".join(lineas) if lineas else "[#8a7f72](sin mensajes)[/]")