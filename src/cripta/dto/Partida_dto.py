from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ResultadoInicio:
    ok: bool
    motivo: str = ""
    semilla_efectiva: int = 0

@dataclass
class SalidaVecina:
    direccion: str
    sala_id: int
    nombre: str
    cerrada: bool
    llave: str
    transitable: bool
    es_salida_final: bool
    tiene_enemigos: bool
    tiene_objetos: bool
    cierre_automatico: int | None = None

@dataclass
class EnemigoPartida:
    id: str
    nombre: str
    vida: int
    ataque: int
    defensa: int
    vida_max: int = 0
    velocidad: int = 100
    comportamiento: str = "errante" # este valor es de respaldo, nunca se usa a menos que creemos un
    # EnemigoPartida sin pasar comportamiento, errante es el mas neutral
    regeneracion: int | None = None
    tipo: str = ""                                          # id de catálogo
    suelta: list[str] = field(default_factory=list)         # botín (§2.6)

@dataclass
class ObjetoSuelo:
    id: str
    nombre: str
    tipo_id: str = ""

@dataclass
class TrampaPartida:
    id: str
    tipo: str
    activa: bool
    dano: int = 0
    rearme: int | None = None
    efecto: str = "daño"

@dataclass
class ObjetoInventario:
    id: str
    nombre: str
    cantidad: int = 1

@dataclass
class SalaModelo:
    id: int
    nombre: str
    descripcion: str
    salidas: list[SalidaVecina] = field(default_factory=list)

@dataclass
class EstadoPartida:
    activa: bool = False
    terminada: bool = False
    victoria: bool = False
    derrota: bool = False

    nombre_jugador: str = ""
    cripta_id: str = ""
    version_cripta: str = ""
    semilla: int = 0
    modo: str = "red"
    presupuesto_solicitudes: int = 0
    inventario_max: int = 10

    acciones_ejecutadas: int = 0
    enemigos_derrotados: int = 0
    reloj_virtual: int = 0
    sala_actual_id: int = 0
    sala_actual_nombre: str = ""
    sala_salida_id: int = 0
    llave_salida: str = ""

    jugador_vida: int = 0
    jugador_vida_max: int = 0
    jugador_ataque: int = 0
    jugador_defensa: int = 0
    jugador_velocidad: int = 0

    vecindad: list[SalidaVecina] = field(default_factory=list)
    enemigos: list[EnemigoPartida] = field(default_factory=list)
    objetos_suelo: list[ObjetoSuelo] = field(default_factory=list)
    trampas: list[TrampaPartida] = field(default_factory=list)
    inventario: list[ObjetoInventario] = field(default_factory=list)
    efectos: list[str] = field(default_factory=list)
    rastro: list[str] = field(default_factory=list)

    salas_conocidas: list[SalaModelo] = field(default_factory=list)
    contenido_cargado: list[int] = field(default_factory=list)
    contenido_pendiente: list[int] = field(default_factory=list)

@dataclass
class CriptaResumen:
    id: str
    nombre: str
    salas: int
    dificultad: int

@dataclass
class DetallesCripta:
    id: str
    version: str
    salas_total: int
    sala_inicial: int
    sala_salida: int
    llave_salida: str
    inventario_max: int
    presupuesto_solicitudes: int
    jugador_vida_max: int
    jugador_ataque: int
    jugador_defensa: int
    jugador_velocidad: int


@dataclass
class ContenidoSala:
    enemigos: list[EnemigoPartida] = field(default_factory=list)
    objetos: list[ObjetoSuelo] = field(default_factory=list)
    trampas: list[TrampaPartida] = field(default_factory=list)
