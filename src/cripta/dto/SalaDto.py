from dataclasses import dataclass, field
from .Salida import Salida


@dataclass
class Sala:
    """Una sala individual del esqueleto.

    `salidas` llega del JSON como objeto {"N": {...}}; aquí se guarda como una
    lista de pares [direccion, Salida] (máx. 4), sin usar dict como estructura (§7).
    """
    id: int
    nombre: str
    salidas: list = field(default_factory=list)

    def __post_init__(self):
        brutas = self.salidas
        self.salidas = []
        if brutas is None:
            return
        # El JSON puede traer un objeto (se recorre solo para leerlo) o ya una lista de pares.
        pares = brutas.items() if hasattr(brutas, "items") else brutas
        for direccion, datos in pares:
            salida = datos if isinstance(datos, Salida) else Salida(**datos)
            self.salidas.append([direccion, salida])

    def obtener_salida(self, direccion: str) -> Salida | None:
        """Busca la salida de una dirección; O(4) como máximo."""
        for d, salida in self.salidas:
            if d == direccion:
                return salida
        return None
