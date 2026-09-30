"""
    src/cripta/controlador/Combate.py
    Contiene la lógica de combate entre actores.
"""

import random

def calcular_danio(atacante, defensor):
    dano = max(
        1,
        atacante.ataque + random.randint(0, 4) - defensor.defensa
    )
    return dano

def aplicar_danio(defensor, dano):
    defensor.vida = max(0, defensor.vida - dano)

def esta_vivo(actor) -> bool:
    """
    Verifica si un actor está vivo.
    """
    return actor.vida > 0

def procesar_muerte(actor, agenda):
    """
    Cancela el próximo evento de un actor cuando este muere.
    """
    if not esta_vivo(actor) and actor._proximo_evento is not None:
        agenda.cancelar(actor._proximo_evento)
        actor._proximo_evento = None