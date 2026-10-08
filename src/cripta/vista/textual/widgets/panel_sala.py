from __future__ import annotations

from textual.markup import escape
from textual.widgets import Static

from cripta.dto.Partida_dto import EstadoPartida

_TITULO = "#e8a33d"
_TENUE = "#8a7f72"
_TEXTO = "#d6cfc4"
_LLAVE = "#c9a227"
_PELIGRO = "#e74c3c"


class PanelSala(Static):
    """Resumen de la sala donde está el jugador."""

    def actualizar(self, p: EstadoPartida) -> None:
        lineas: list[str] = [
            f"[bold {_TITULO}]{escape(p.sala_actual_nombre)}[/]  (sala {p.sala_actual_id})",
            "",
            f"[bold {_TITULO}]SALIDAS[/]",
        ]
        lineas.extend(self._lineas_salidas(p))
        lineas.append("")
        lineas.append(f"[bold {_TITULO}]ENEMIGOS[/]")
        lineas.extend(self._lineas_enemigos(p))
        lineas.append("")
        lineas.append(f"[bold {_TITULO}]SUELO[/]")
        lineas.extend(self._lineas_suelo(p))
        self.update("\n".join(lineas))

    @staticmethod
    def _lineas_salidas(p: EstadoPartida) -> list[str]:
        if not p.vecindad:
            return [f"[{_TENUE}](sin salidas)[/]"]
        lineas: list[str] = []
        for v in p.vecindad:
            if v.cerrada:
                estado = f"cerrada, llave: {escape(v.llave or '?')}"
                color = _LLAVE
            else:
                estado = "abierta"
                color = _TEXTO
            if v.cierre_automatico:
                estado += f", se cierra sola a las {v.cierre_automatico} u."
            final = "  (SALIDA FINAL)" if v.es_salida_final else ""
            lineas.append(
                f"[{color}]{v.direccion} -> {v.sala_id}  {escape(v.nombre)}  ({estado}){final}[/]"
            )
        return lineas

    @staticmethod
    def _lineas_enemigos(p: EstadoPartida) -> list[str]:
        if not p.enemigos:
            return [f"[{_TENUE}](sin enemigos)[/]"]
        lineas: list[str] = []
        for e in p.enemigos:
            lineas.append(
                f"[{_PELIGRO}]![/] {escape(e.nombre)} ({escape(e.id)})  HP {e.vida}/{e.vida_max}"
            )
        return lineas

    @staticmethod
    def _lineas_suelo(p: EstadoPartida) -> list[str]:
        if not p.objetos_suelo:
            return [f"[{_TENUE}](nada)[/]"]
        return [f"* {escape(o.nombre)}" for o in p.objetos_suelo]