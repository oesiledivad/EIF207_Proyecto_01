"""DTO de la consulta de la línea de tiempo (spec 004, FR-005)."""

from __future__ import annotations

from dataclasses import dataclass, field

from cripta.dto.Conocimiento_dto import MapaConocido


@dataclass
class EnemigoInstante:
    id: str
    nombre: str
    vida: int
    vida_max: int


@dataclass
class ResumenInstante:
    reloj: int
    acciones: int                 # acciones del jugador ya tomadas en ese estado
    sala_id: int
    sala_nombre: str
    vida: int
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int
    resultado: str                # en curso, victoria o derrota
    inventario: list[str] = field(default_factory=list)
    efectos: list[str] = field(default_factory=list)
    enemigos: list[EnemigoInstante] = field(default_factory=list)
    mapa: MapaConocido = field(default_factory=MapaConocido)
    aviso: str = ""               # por ejemplo, que la partida terminó antes (FR-022)


@dataclass
class ResultadoHistoria:
    ok: bool
    motivo: str = ""
    resumen: ResumenInstante | None = None
