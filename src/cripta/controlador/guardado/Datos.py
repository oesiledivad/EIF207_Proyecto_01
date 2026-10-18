"""Estructuras intermedias del guardado.

Sirven de puente entre los bytes del archivo y los objetos del modelo: la lectura
las llena y valida, y la restauración las vuelca sobre la partida.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cripta.estructuras.Inventario import ItemInventario


@dataclass
class Cuerpo:
    sala_id: int
    bytes_: bytes


@dataclass
class ActorG:
    identificador: str
    vida: int
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int
    velocidad_base: int
    sala: int
    tiempo_siguiente: int | None
    dano_veneno: int
    fin_veneno: int | None
    regeneracion_cantidad: int


@dataclass
class EnemigoG:
    actor: ActorG
    nombre: str
    comportamiento: str
    tipo: str
    suelta: list[str]
    regeneracion_objetivo: int | None


@dataclass
class SalaG:
    sala_id: int
    ultimo_tiempo_visita: int | None
    contenido_cargado: bool
    salidas: list[list[str, bool]]
    enemigos: list[EnemigoG]
    objetos: list[list[str, str, str]]
    trampas: list[list[str, bool, int, int | None, str, str]]


@dataclass
class EventoG:
    tiempo: int
    secuencia: int
    tipo: str
    clase_actor: int
    sala_id: int
    clave: str


@dataclass
class DatosGuardado:
    version_cripta: str
    nombre_jugador: str = ""
    cripta_id: str = ""
    semilla: int = 0
    modo: str = ""
    acciones_ejecutadas: int = 0
    enemigos_derrotados: int = 0
    sala_actual_id: int = 0
    tiempo_actual: int = 0
    salidas_abiertas: list[list] = field(default_factory=list)
    azar_version: int = 3
    azar_interno: list[int] = field(default_factory=list)
    azar_gauss: float | None = None
    jugador: ActorG | None = None
    inventario_max: int = 10
    antorcha_encendida: bool = False
    capacidad_inventario: int = 10
    items: list[ItemInventario] = field(default_factory=list)
    item_actual: str | None = None
    eventos: list[EventoG] = field(default_factory=list)
    salas: list[SalaG] = field(default_factory=list)