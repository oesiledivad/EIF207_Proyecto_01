from .CatalogoDto import FichaCatalogo


class FichaAntorcha(FichaCatalogo):
    def __init__(self, id:str, nombre:str, clase:str, peso:int, valor:int, duracion:int):
        super().__init__(id,nombre,clase)
        self.peso = peso
        self.valor = valor
        self.duracion = duracion

    @staticmethod
    def desde_dict(d: dict) -> "FichaAntorcha":
        return FichaAntorcha(
            id=d["id"],
            nombre=d["nombre"],
            clase=d["clase"],
            peso=d["peso"],
            valor=d["valor"],
            duracion=d["duracion"],
        )