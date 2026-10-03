"""Panel de inventario."""

from __future__ import annotations

from textual.widgets import Static

from cripta.controlador.Aplicacion import EstadoPartida


class PanelInventario(Static):
    def actualizar(self, p: EstadoPartida) -> None:
        if not p.inventario:
            self.update(f"[#8a7f72](vacío)  {len(p.inventario)}/{p.inventario_max}[/]")
            return
        lineas = []
        for i, item in enumerate(p.inventario):
            marca = "[A]" if item.get("equipado_arma") else (
                "[D]" if item.get("equipado_armadura") else "   "
            )
            lineas.append(f"{marca} {item.get('nombre', '?')}")
        lineas.append(f"\n[#8a7f72]{len(p.inventario)}/{p.inventario_max}[/]")
        self.update("\n".join(lineas))