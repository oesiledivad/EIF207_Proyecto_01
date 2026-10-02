"""
    src/cripta/controlador/Combate.py
    Contiene la lógica de combate entre actores.
"""

def calcular_danio(atacante, defensor, azar):
    """
        Calcula el daño usando el ataque, la defensa y el azar.

        ``azar`` se recibe como una instancia de random.Random para
        mantener el azar controlado desde la simulación.
        """
    dano = max(
        1,
        atacante.ataque + azar.randint(0, 4) - defensor.defensa
    )
    return dano

def aplicar_danio(defensor, dano):
    """
    Aplica el daño a un defensor.
    """
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