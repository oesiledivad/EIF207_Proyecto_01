
from .SalaDto import Sala   # o el nombre exacto de tu archivo/clase
from .Salida import Salida

class EsqueletoSala:
    """Wrapper de GET /criptas/{id}/salas?pagina=n (una página del esqueleto)."""
    def __init__(self, pagina: int, total_paginas: int, salas: list) -> None:
        self.pagina = pagina
        self.total_paginas = total_paginas
        self.salas = salas  # list[Sala]

    @staticmethod
    def desde_dict(d: dict) -> "EsqueletoSala":
        salas = []
        for sala_dict in d["salas"]:
            salas.append(Sala.desde_dict(sala_dict))
        return EsqueletoSala(
            pagina=d["pagina"],
            total_paginas=d["total_paginas"],
            salas=salas,
        )