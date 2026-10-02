from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo


@dataclass
class FichaPocion(FichaCatalogo):
    peso: int
    valor: int
    cura: int | None = None
    modificador_velocidad: int | None = None
    duracion: int | None = None