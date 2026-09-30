

class FichaCatalogo:
    """Base: campos comunes a toda ficha de catálogo."""
    def __init__(self, id: str, nombre: str, clase: str) -> None:
        self.id = id
        self.nombre = nombre
        self.clase = clase

