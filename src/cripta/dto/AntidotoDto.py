from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo

@dataclass
class FichaAntidoto(FichaCatalogo):
    peso: int
    valor: int