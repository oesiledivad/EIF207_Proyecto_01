"""
La clase Guardian representa a un enemigo que protege la salida del laberinto.
Hereda de la clase Enemy y tiene atributos y métodos específicos para 
su comportamiento en el juego.

"""
from modelo.Enemigo import Enemigo
class Guardian(Enemigo):
    def __init__( identificador,
            vida,
            vida_max,
            ataque,
            defensa,
            velocidad,
            sala,
            tiempo_siguiente,
            comportamiento) -> None:
        super().__init__(identificador, vida, vida_max, ataque, defensa, velocidad, sala, tiempo_siguiente)
        
    """
    metodos especificos de guardian
    """