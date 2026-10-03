from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo

@dataclass
class FichaTrampa(FichaCatalogo):
    daño: int
    rearme: int | None = None