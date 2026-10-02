"""
    src/cripta/modelo/actor.py
    Clase base para representar a los actores de la partida.
"""

class Actor:
    def __init__(self, identificador, vida, vida_max, ataque, defensa, velocidad, sala,tiempo_siguiente):
        self.identificador = identificador
        self.vida = vida
        self.vida_max = vida_max
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad = velocidad
        self.sala = sala
        self.tiempo_siguiente = tiempo_siguiente

        # Referencia al evento que tiene programado actualmente.
        # Se utiliza para poder cancelarlo y reprogramarlo en el metodo
        # reprogramar_tiempo_siguiente de la agenda de eventos.
        self._proximo_evento = None