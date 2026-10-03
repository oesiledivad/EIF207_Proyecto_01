from dto.Crypta_Details import Crypta_Details
from modelo.Jugador import Jugador


def ensamblar_jugador(detalles: Crypta_Details) -> Jugador:
    return Jugador(
        identificador="jugador",
        vida=detalles.jugador.vida_max,
        vida_max=detalles.jugador.vida_max,
        ataque=detalles.jugador.ataque,
        defensa=detalles.jugador.defensa,
        velocidad=detalles.jugador.velocidad,
        sala=detalles.sala_inicial,              # antes: room_start
        tiempo_siguiente=None,
        inventario_max=detalles.inventario_max,  # antes: inventario
    )