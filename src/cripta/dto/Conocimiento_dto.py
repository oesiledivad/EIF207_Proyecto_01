"""DTO del conocimiento del jugador y del viaje automático (FR-018, FR-031)."""

from dataclasses import dataclass, field


@dataclass
class SalidaConocida:
    direccion: str
    destino: int
    costo: int
    puerta: str            # abierta, cerrada o sin_observar
    destino_estado: str    # explorada o avistada


@dataclass
class SalaConocida:
    id: int
    nombre: str
    salidas: list[SalidaConocida] = field(default_factory=list)


@dataclass
class MapaConocido:
    exploradas: list[SalaConocida] = field(default_factory=list)
    avistadas: list[int] = field(default_factory=list)   # solo el id (FR-004)


@dataclass
class ResultadoViaje:
    ok: bool                # orden aceptada o paso dado
    activo: bool            # el viaje continúa
    motivo: str = ""        # código de detención, o vacío
    mensaje: str = ""       # texto para la bitácora
