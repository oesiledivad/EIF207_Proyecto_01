from .CatalogoDto import FichaCatalogo


class FichaTrampa(FichaCatalogo):
    def __init__(self, id: str, nombre: str, clase: str, dano: int, rearme: int) -> None:
        super().__init__(id, nombre, clase)
        self.dano = dano
        self.rearme = rearme

    @staticmethod
    def desde_dict(d: dict) -> "FichaTrampa":
        return FichaTrampa(
            id=d["id"],
            nombre=d["nombre"],
            clase=d["clase"],
            dano=d["daño"],
            rearme=d["rearme"],
        )