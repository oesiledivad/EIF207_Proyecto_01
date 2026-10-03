from dataclasses import dataclass

@dataclass
class FichaCatalogo:
    """Base: campos comunes a toda ficha de catálogo."""
    id: str
    nombre: str
    clase: str