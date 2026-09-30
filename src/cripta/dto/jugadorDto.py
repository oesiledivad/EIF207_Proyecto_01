# dto/JugadorDto.py  (o el nombre que uses para consistencia con tus otros archivos *Dto.py)

class Jugador:
    """DTO: stats iniciales del jugador, viene anidado dentro de crypta_details."""

    def __init__(self, vida_max: int, ataque: int, defensa: int, velocidad: int) -> None:
        self.vida_max = vida_max
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad = velocidad

    @staticmethod
    def desde_dict(d: dict) -> "Jugador":
        return Jugador(
            vida_max=d["vida_max"],
            ataque=d["ataque"],
            defensa=d["defensa"],
            velocidad=d["velocidad"],
        )