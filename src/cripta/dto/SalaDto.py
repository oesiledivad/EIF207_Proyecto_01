

from .Salida import Salida


class Sala:
    """Una sala individual del esqueleto."""
    def __init__(self, id: int, nombre: str, salidas: dict) -> None:
        self.id = id
        self.nombre = nombre
        self.salidas = salidas

    @staticmethod
    def desde_dict(d: dict) -> "Sala":
        salidas = {}
        for direccion, salida_dict in d["salidas"].items():
            salidas[direccion] = Salida.desde_dict(salida_dict)
        return Sala(id=d["id"], nombre=d["nombre"], salidas=salidas)
