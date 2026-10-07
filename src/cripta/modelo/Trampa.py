class TrampaJuego:
    def __init__(self, instancia: str, armada: bool, dano: int, rearme: int, efecto: str = "daño",
                 tipo: str = "") -> None:
        self.instancia = instancia
        self.armada = armada
        self.dano = dano
        self.rearme = rearme
        self.efecto = efecto
        self.tipo = tipo  # id de catálogo (para proteger su ficha mientras sea la sala actual)
