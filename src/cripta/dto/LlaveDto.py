from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo

@dataclass
class FichaLlave(FichaCatalogo):
    peso: int
    valor: int
    abre: str | int | None = None