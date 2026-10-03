from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo

@dataclass
class FichaAntorcha(FichaCatalogo):
    peso: int
    valor: int
    duracion: int