from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo

@dataclass
class FichaEnemigo(FichaCatalogo):
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int
    comportamiento: str          # "guardián" | "errante" | "rastreador"
    suelta: list[str] | None = None