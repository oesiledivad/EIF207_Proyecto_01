from .CatalogoDto import FichaCatalogo

class FichaPergaminoRetorceso(FichaCatalogo):
    def __init__(self, id: str, nombre: str, clase: str, peso: int, valor: int) -> None:
        super().__init__(id, nombre, clase)
        self.peso = peso
        self.valor = valor

    @staticmethod
    def desde_dict(d: dict) -> "FichaPergaminoRetorceso":
        return FichaPergaminoRetorceso(
            id=d["id"],
            nombre=d["nombre"],
            clase=d["clase"],
            peso=d["peso"],
            valor=d["valor"],
            
        )