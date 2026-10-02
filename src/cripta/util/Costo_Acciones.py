# src/cripta/util/costos_acciones.py
"""Costos base de acciones (§2.3) y fórmulas de intervalo/reescalado."""

COSTOS = {
    "mover": 100,
    "atacar": 100,
    "esperar": 100,
    "usar_objeto": 50,
    "equipar_objeto": 50,
    "recoger": 25,
    "soltar": 25,
    "abrir_puerta": 50,
}

def calcular_intervalo(costo: int, velocidad: int) -> int:
    """intervalo = max(1, costo * 100 // velocidad)"""
    return max(1, costo * 100 // velocidad)

def reescalar_tiempo_siguiente(tiempo_siguiente: int, t: int,
                                velocidad_anterior: int, velocidad_nueva: int) -> int:
    """§2.3 — cambio de velocidad con acción ya programada."""
    restante = tiempo_siguiente - t
    restante_nuevo = max(1, restante * velocidad_anterior // velocidad_nueva)
    return t + restante_nuevo