from modelo.enemigos.Rastreador import Rastreador
from modelo.enemigos.Guardian import Guardian
from modelo.enemigos.Errante import Errante
from dto.EnemigoDto import FichaEnemigo


def ensamblar_enemigo(colocacion, ficha, sala_id):
    if not isinstance(ficha, FichaEnemigo):
        raise TypeError("El objeto proporcionado no es una instancia de FichaEnemigo")

    # si la API no manda vida, el enemigo nace con la vida máxima
    vida = colocacion.vida if colocacion.vida is not None else ficha.vida_max
# aca lo que hacemos es decidir que clase de enemigo vamos a instanciar según el comportamiento que tenga la ficha  
#
    match ficha.comportamiento:
        case "guardián":   clase = Guardian
        case "errante":    clase = Errante
        case "rastreador": clase = Rastreador
        case c:
            raise ValueError(f"Comportamiento desconocido: {c}")

    return clase(
        colocacion.instancia, vida, ficha.vida_max,
        ficha.ataque, ficha.defensa, ficha.velocidad,
        sala_id, None, ficha.comportamiento,
    )