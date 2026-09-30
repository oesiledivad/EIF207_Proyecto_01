
from .CatalogoDto import FichaCatalogo

class FichaEnemigo(FichaCatalogo):
    def __init__(self, id: str, nombre: str, clase: str, vida_max: int,
                 ataque: int, defensa: int, velocidad: int,
                 comportamiento: str, suelta: list) -> None:
        super().__init__(id, nombre, clase)
        self.vida_max = vida_max
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad = velocidad
        self.comportamiento = comportamiento
        self.suelta = suelta

    @staticmethod
    def desde_dict(d: dict) -> "FichaEnemigo":
        return FichaEnemigo(
            id=d["id"], nombre=d["nombre"], clase=d["clase"],
            vida_max=d["vida_max"], ataque=d["ataque"], defensa=d["defensa"],
            velocidad=d["velocidad"], comportamiento=d["comportamiento"],
            suelta=d.get("suelta", []),
        )