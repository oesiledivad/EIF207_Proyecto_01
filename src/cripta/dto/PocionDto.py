from .CatalogoDto import FichaCatalogo
class FichaPocion(FichaCatalogo):
    def __init__(self, id:str, nombre:str, clase:str,efecto:str, duracion:int, peso:int, valor:int
                 ):
        super().__init__(id,nombre,clase)
        self.peso = peso
        self.valor = valor
        self.efecto = efecto
        self.duracion = duracion

    @staticmethod
    def desde_dict(d: dict) -> "FichaPocion":
        return FichaPocion(
            id=d["id"],
            nombre=d["nombre"],
            clase=d["clase"],
            peso=d["peso"],
            valor=d["valor"],
            efecto=d["efecto"],
            duracion=d["duracion"]
        )