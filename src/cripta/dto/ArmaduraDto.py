from .CatalogoDto import FichaCatalogo
class FichaArmadura(FichaCatalogo):
    def __init__(self, id:str, nombre:str, clase:str, peso:int,valor:int, defensa_bonus:int):
        super().__init__(id, nombre, clase)
        self.peso = peso
        self.valor = valor
        self.defensa_bonus = defensa_bonus

    @staticmethod
    def desde_dict(d: dict) -> "FichaArmadura":
        return FichaArmadura(
            id=d["id"],
            nombre=d["nombre"],
            clase=d["clase"],
            peso=d["peso"],
            valor=d["valor"],
            defensa_bonus=d["defensa_bonus"],
        )