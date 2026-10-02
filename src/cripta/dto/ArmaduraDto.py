from dataclasses import dataclass
from .CatalogoDto import FichaCatalogo

@dataclass
class FichaArmadura(FichaCatalogo):
    peso: int
    valor: int
    defensa_bonus: int