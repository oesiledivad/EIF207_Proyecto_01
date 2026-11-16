"""DTO de la verificación de resolubilidad de una cripta.

Son dataclasses sin lógica ni datos de una cripta concreta. El modelo recibe
`UbicacionLlave` ya parseadas y devuelve un `ResultadoVerificacion`.

Cumple: FR-002, FR-007, FR-009 a FR-012.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class UbicacionLlave:
    """Ubicación publicada de una llave.

    Los ids de llave se comparan como cadenas, carácter por carácter, y los
    ids de sala como enteros.
    """
    llave: str                      # Id de la llave, no vacío
    sala: int                       # Id de sala; si no existe en el esqueleto, la ubicación se descarta con advertencia
    enemigo: str | None = None      # Id de la instancia que la suelta; None si está en el suelo


@dataclass
class LlaveEnOrden:
    """Una llave del orden de obtención."""
    llave: str
    sala: int                       # Sala donde se obtuvo
    enemigo: str | None = None
    ronda: int = 0


@dataclass
class PuertaBloqueada:
    """Puerta cerrada que exige una llave."""
    sala_origen: int
    direccion: str
    sala_destino: int
    llave: str                      # Llave requerida


@dataclass
class PasoCiclo:
    """Un paso de un ciclo de dependencias entre llaves."""
    llave: str
    sala: int                       # Ubicación usada
    enemigo: str | None
    puerta: PuertaBloqueada         # Puerta testigo que exige la llave siguiente


@dataclass
class Ciclo:
    """Ciclo de dependencias; el paso final apunta a la llave inicial."""
    pasos: list[PasoCiclo] = field(default_factory=list)


@dataclass
class LlaveBloqueada:
    """Llave inobtenible con su causa.

    `causa` es `en_ciclo`, `depende_de`, `sin_ubicacion`, `sala_desconectada`
    o `ubicacion_invalida`.
    """
    llave: str
    ubicaciones: list[UbicacionLlave] = field(default_factory=list)   # Todas las publicadas
    causa: str = ""
    depende_de: str | None = None   # Llave de la que depende, con la causa `depende_de`


@dataclass
class ReporteBloqueo:
    """Explicación de por qué la cripta no se puede ganar."""
    motivo: str                     # "llave_salida_inobtenible" o "puerta_sin_destino"
    llaves_inobtenibles: list[LlaveBloqueada] = field(default_factory=list)
    frontera: list[PuertaBloqueada] = field(default_factory=list)
    ciclos: list[Ciclo] = field(default_factory=list)


@dataclass
class EstadisticasVerificacion:
    """Contadores de la exploración, para pruebas de complejidad sin tiempo."""
    salas_encoladas: int = 0
    salidas_examinadas: int = 0
    llaves_obtenidas: int = 0


@dataclass
class ResultadoVerificacion:
    """Resultado de verificar una cripta.

    `estado` es "resoluble", "no_resoluble" o "no_verificable".
    """
    estado: str
    orden_llaves: list[LlaveEnOrden] = field(default_factory=list)   # Solo con `resoluble`; vacía en los otros casos
    reporte: ReporteBloqueo | None = None                            # Solo con `no_resoluble`
    motivo_no_verificable: str = ""                                  # Solo con `no_verificable`
    advertencias: list[str] = field(default_factory=list)
    cripta_id: str = ""
    version: str = ""
    estadisticas: EstadisticasVerificacion | None = None
