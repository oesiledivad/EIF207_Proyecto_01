

from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo

@dataclass
class FichaPergaminoRetroceso(FichaCatalogo):
    peso: int
    valor: int