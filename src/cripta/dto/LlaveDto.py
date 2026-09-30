from .CatalogoDto import FichaCatalogo

class FichaLlave(FichaCatalogo):
    def __init__(self, id: str, nombre: str, clase: str, abre: bool, peso: int, valor: int) -> None:
        super().__init__(id, nombre, clase)
        self.peso = peso
        self.valor = valor
        self.abre = abre

    @staticmethod
    def desde_dict(d: dict) -> "FichaLlave":
        return FichaLlave(
            id=d["id"],
            nombre=d["nombre"],
            clase=d["clase"],
            abre=d["abre"],
            peso=d["peso"],
            valor=d["valor"],
        )