"""Panel de inventario.

Muestra la lista completa del inventario en orden real, marca el item
actual y los equipados, e indica la capacidad usada. Las vistas
ordenables no alteran el orden real
"""

from __future__ import annotations

from textual.widgets import Static

from cripta.estructuras.Inventario import Inventario, ItemInventario


class PanelInventario(Static):
    """Vista del inventario del jugador."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._criterio: str = "real"

    def set_criterio(self, criterio: str) -> None:
        """Cambia la vista ordenable activa.

        Args:
            criterio: real, peso, valor o nombre.
        """
        self._criterio = criterio

    def actualizar(
        self,
        inventario: Inventario | None,
        item_actual: ItemInventario | None,
    ) -> None:
        if inventario is None:
            self.update("[#8a7f72](inventario no inicializado)[/]")
            return

        items = self._items_segun_criterio(inventario)
        if not items:
            self.update(
                f"[#8a7f72](vacío)  {inventario.tamano}/{inventario.capacidad}[/]"
            )
            return

        lineas: list[str] = []
        for item in items:
            marca_actual = ">" if item_actual is not None and item.instancia_id == item_actual.instancia_id else " "
            marca_equipo = "[A]" if item.clase == "arma" and item.equipado else (
                "[D]" if item.clase == "armadura" and item.equipado else "   "
            )
            color = "#e8a33d" if marca_actual == ">" else "#d6cfc4"
            lineas.append(f"[{color}]{marca_actual} {marca_equipo} {item.nombre}[/]")

        encabezado = {
            "real": "orden real",
            "peso": "por peso",
            "valor": "por valor",
            "nombre": "por nombre",
        }.get(self._criterio, "orden real")

        lineas.append("")
        lineas.append(
            f"[#8a7f72]{inventario.tamano}/{inventario.capacidad}  "
            f"({encabezado})  [P]eso [V]alor [N]ombre [R]eal[/]"
        )
        self.update("\n".join(lineas))

    def _items_segun_criterio(self, inventario: Inventario) -> list[ItemInventario]:
        if self._criterio == "peso":
            return inventario.vista_por_peso()
        if self._criterio == "valor":
            return inventario.vista_por_valor()
        if self._criterio == "nombre":
            return inventario.vista_por_nombre()
        return inventario.items()