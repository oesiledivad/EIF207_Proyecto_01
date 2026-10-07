class TrampaJuego:
    def __init__(self, instancia: str, armada: bool, dano: int, rearme: int, efecto: str = "daño") -> None:
        self.instancia = instancia
        self.armada = armada
        self.dano = dano
        self.rearme = rearme
        self.efecto = efecto