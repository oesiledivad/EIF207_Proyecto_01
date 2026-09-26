


class Crypta_all:
    """Una cripta de la lista devuelta por GET /criptas"""
    def __init__(self, id: str, nombre: str, salas: int, dificultad: int) -> None:
        self.id = id
        self.nombre = nombre
        self.salas = salas
        self.dificultad = dificultad
    @staticmethod
    def since_dict(d: dict) -> "Crypta_all":
        return Crypta_all(
            id=d["id"],
            nombre=d["nombre"],
            salas=d["salas"],
            dificultad=d["dificultad"],
        )

