from dataclasses import dataclass

@dataclass
class Jugador:
    """DTO: stats iniciales del jugador, viene anidado dentro de crypta_details."""
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int