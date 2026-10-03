from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo


@dataclass
class FichaArma(FichaCatalogo):
    peso: int
    valor: int
    ataque_bonus: int