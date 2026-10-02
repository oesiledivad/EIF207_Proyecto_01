from modelo.Enemigo import Enemigo
from modelo.enemigos.Rastreador import Rastreador
from modelo.enemigos.Guardian import Guardian
from modelo.enemigos.Errante import Errante
from dto.EnemigoDto import FichaEnemigo


def ensamblar_enemigo(dto_instancia, ficha, sala_id):
    if not isinstance(ficha, FichaEnemigo):
        raise TypeError("El objeto proporcionado no es una instancia de FichaEnemigo")
    comportamiento = ficha.comportamiento
    if comportamiento == "guardián":
        return Guardian(
            dto_instancia.instancia,
            dto_instancia.vida,
            ficha.vida_max,
            ficha.ataque,
            ficha.defensa,
            ficha.velocidad,
            sala_id,
            None,
            comportamiento,
        )
    elif comportamiento == "errante":
        return Errante(
            dto_instancia.instancia,
            dto_instancia.vida,
            ficha.vida_max,
            ficha.ataque,
            ficha.defensa,
            ficha.velocidad,
            sala_id,
            None,
            comportamiento,
        )
    elif comportamiento == "rastreador":
        return Rastreador(
            dto_instancia.instancia,
            dto_instancia.vida,
            ficha.vida_max,
            ficha.ataque,
            ficha.defensa,
            ficha.velocidad,
            sala_id,
            None,
            comportamiento,
        )
    else:
        raise ValueError(f"Comportamiento desconocido: {comportamiento}")
