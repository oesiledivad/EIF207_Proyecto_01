from .CatalogoDto import FichaCatalogo

class FichaTrampa   (FichaCatalogo):
    def __init__(self, id:str,nombre:str,clase:str,peso:int, valor:int, ataque_bonus:int):
        super().__init__(id,nombre,clase)
        self.peso = peso
        self.valor = valor
        self.ataque_bonus = ataque_bonus
    @staticmethod
    def desde_dict(d: dict) -> "FichaTrampa":
        return FichaTrampa(
            id=d["id"],
            nombre=d["nombre"],
            clase=d["clase"],
            peso=d["peso"],
            valor=d["valor"],
            ataque_bonus=d["ataque_bonus"],
        )