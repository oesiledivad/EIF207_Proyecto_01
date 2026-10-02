

from dataclasses import dataclass, field
from .Salida import Salida

@dataclass
class Sala:
    """Una sala individual del esqueleto."""
    id: int
    nombre: str
    salidas: dict[str, Salida] = field(default_factory=dict)
  
    def __post_init__(self):
        # 1. Si la API no mandó "salidas", partimos de un diccionario vacío
        if self.salidas is None:
            self.salidas = {}

        # 2. Aquí iremos guardando las salidas ya convertidas
        salidas_convertidas = {}

        # 3. Recorremos cada salida que llegó
        for direccion, datos in self.salidas.items():

            if isinstance(datos, Salida):
                # ya es una Salida, la dejamos como está
                salidas_convertidas[direccion] = datos
            else:
                # es un diccionario, lo convertimos en Salida
                salidas_convertidas[direccion] = Salida(**datos)

        # 4. Reemplazamos el contenido original por el ya convertido
        self.salidas = salidas_convertidas