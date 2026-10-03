
class Catalogo_Lista:
    def __init__(self, fichas=None):
        self._fichas = list(fichas or [])

    def agregar(self, ficha):
        self._fichas.append(ficha)

    def obtener(self, id_tipo):
        for f in self._fichas:
            if f.id == id_tipo:
                return f
        raise KeyError(f"Ficha no encontrada: {id_tipo}")