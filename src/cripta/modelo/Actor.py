"""
    src/cripta/modelo/Actor.py
    Clase base para representar a los actores de la partida.
"""

from cripta.util.Costo_Acciones import reescalar_tiempo_siguiente

class Actor:
    """
    Clase base para representar a los actores de la partida.
    Puede ser jugador o enemigo.
    """
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
        self.evento_veneno = None
        self.dano_veneno = 0
        self.fin_veneno = None
        self.velocidad_base = velocidad  # para restaurar tras un efecto temporal
        self.evento_fin_velocidad = None
        self.evento_regeneracion = None
        self.regeneracion_cantidad = 0

    def actualizar_velocidad(self, nueva_velocidad: int, tiempo_actual: int, agenda) -> None:
        if self._proximo_evento is not None and self._proximo_evento.valido:
            nuevo_tiempo = reescalar_tiempo_siguiente(
                self._proximo_evento.tiempo_siguiente, tiempo_actual,
                self.velocidad, nueva_velocidad
        )
            agenda.reprogramar(self, nuevo_tiempo, self._proximo_evento.tipo)
        agenda.cambiar(self, "velocidad", nueva_velocidad)