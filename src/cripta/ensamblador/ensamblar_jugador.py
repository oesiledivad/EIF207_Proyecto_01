from src.cripta.dto import Crypta_Details
from src.cripta.modelo.jugador import Jugador

@staticmethod
def ensamblarJugador(datos: Crypta_Details) -> Jugador:
    return Jugador(
        identificador="jugador",
        vida=datos.jugador.vida_max,
        vida_max=datos.jugador.vida_max,
        ataque=datos.jugador.ataque,
        defensa=datos.jugador.defensa,
        velocidad=datos.jugador.velocidad,
        sala=datos.room_start,
        tiempo_siguiente=None,
        inventario_max=datos.inventario,
    )