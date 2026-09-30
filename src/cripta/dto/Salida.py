class Salida:
    """Una salida dentro de una sala."""
    def __init__(self, sala_destino: int, cerrada: bool = False,
                 llave: str = None, cierre_automatico: int = None) -> None:
        self.sala_destino = sala_destino
        self.cerrada = cerrada
        self.llave = llave
        self.cierre_automatico = cierre_automatico

    @staticmethod
    def desde_dict(d: dict) -> "Salida":
        return Salida(
            sala_destino=d["sala"],
            cerrada=d.get("cerrada", False),
            llave=d.get("llave"),
            cierre_automatico=d.get("cierre_automatico"),
        )
