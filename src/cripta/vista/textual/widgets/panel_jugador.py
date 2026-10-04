"""Panel de estado del jugador."""

from __future__ import annotations

from textual.widgets import Static

from cripta.controlador.Aplicacion import EstadoPartida


def _barra(actual: int, total: int, ancho: int = 10) -> str:
    if total <= 0:
        return "░" * ancho
    llenos = int(ancho * actual / total)
    return "█" * llenos + "░" * (ancho - llenos)


class PanelJugador(Static):
    def actualizar(self, p: EstadoPartida) -> None:
        hp = _barra(p.jugador_vida, p.jugador_vida_max)
        texto = (
            f"{p.nombre_jugador}\n"
            f"HP  {hp} {p.jugador_vida}/{p.jugador_vida_max}\n"
            f"ATQ {p.jugador_ataque}\n"
            f"DEF {p.jugador_defensa}\n"
            f"VEL {p.jugador_velocidad}\n"
        )
        self.update(texto)