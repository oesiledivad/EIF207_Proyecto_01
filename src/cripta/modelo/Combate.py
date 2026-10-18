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
    if getattr(defensor, "invulnerable", False):
        return 0
    if getattr(atacante, "insta_kill", False):
        return max(0, defensor.vida)
    dano = max(
        1,
        atacante.ataque + azar.randint(0, 4) - defensor.defensa
    )
    return dano

def aplicar_danio(defensor, dano, agenda=None):
    """
    Aplica el daño a un defensor.
    """
    # Punto común para ataques, trampas y veneno; God Mode protege todas las fuentes.
    if getattr(defensor, "invulnerable", False):
        return
    vida = max(0, defensor.vida - dano)
    if agenda is None:
        defensor.vida = vida
    else:
        agenda.cambiar(defensor, "vida", vida)

def esta_vivo(actor) -> bool:
    """
    Verifica si un actor está vivo.
    """
    return actor.vida > 0

def procesar_muerte(actor, agenda) -> None:
    """Cancela todos los eventos pendientes de un actor que acaba de morir (§2.6)."""
    for atributo in ("_proximo_evento", "evento_veneno", "evento_regeneracion", "evento_fin_velocidad", "evento_antorcha"):
        evento = getattr(actor, atributo, None)
        if evento is not None:
            agenda.cancelar(evento)
            agenda.cambiar(actor, atributo, None)

