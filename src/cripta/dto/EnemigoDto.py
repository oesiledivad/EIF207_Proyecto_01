from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo

@dataclass
class FichaEnemigo(FichaCatalogo):
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int
    comportamiento: str          # "guardián" | "errante" | "rastreador" | "cazador"
    suelta: list[str] | None = None
    regeneracion: int | None = None
    rango: int | None = None     # solo cazador: costo máximo de la ruta que persigue (FR-008)
