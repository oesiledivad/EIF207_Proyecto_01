"""Barra superior con cripta, versión, reloj, modo y solicitudes."""

from __future__ import annotations

from textual.widgets import Static

from cripta.controlador.Aplicacion import EstadoPartida
from cripta.estructuras.Ordenamientos import ordenar


class BarraSuperior(Static):
    def actualizar(
        self,
        p: EstadoPartida,
        usadas: int,
        animacion: int = 0,
    ) -> None:
        pendientes = ""
        if p.contenido_pendiente:
            puntos = "." * max(1, animacion)
            salas = ",".join(str(s) for s in ordenar(list(p.contenido_pendiente)))
            pendientes = f"  [CARGANDO{puntos} salas {salas}]"
        self.update(
            f"CRIPTA · {p.cripta_id} · v {p.version_cripta}"
            f"    t = {p.reloj_virtual}  [virtual]"
            f"    modo: {p.modo}"
            f"    solicitudes: {usadas}/{p.presupuesto_solicitudes}"
            f"{pendientes}"
        )