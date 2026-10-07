# src/cripta/util/costos_acciones.py
"""Costos base de acciones (§2.3) y fórmulas de intervalo/reescalado.

Antes era un dict COSTOS; se cambió a constantes + match para no usar
dict como tabla de búsqueda (§7).
"""

COSTO_MOVER = 100
COSTO_ATACAR = 100
COSTO_ESPERAR = 100
COSTO_USAR_OBJETO = 50
COSTO_EQUIPAR_OBJETO = 50
COSTO_RECOGER = 25
COSTO_SOLTAR = 25
COSTO_ABRIR_PUERTA = 50


def costo_accion(accion: str) -> int:
    """Devuelve el costo base de una acción (§2.3). O(1)."""
    match accion:
        case "mover":
            return COSTO_MOVER
        case "atacar":
            return COSTO_ATACAR
        case "esperar":
            return COSTO_ESPERAR
        case "usar_objeto":
            return COSTO_USAR_OBJETO
        case "equipar_objeto":
            return COSTO_EQUIPAR_OBJETO
        case "recoger":
            return COSTO_RECOGER
        case "soltar":
            return COSTO_SOLTAR
        case "abrir_puerta":
            return COSTO_ABRIR_PUERTA
    raise ValueError(f"Acción sin costo definido: {accion!r}")


def calcular_intervalo(costo: int, velocidad: int) -> int:
    """intervalo = max(1, costo * 100 // velocidad)"""
    return max(1, costo * 100 // velocidad)


def reescalar_tiempo_siguiente(tiempo_siguiente: int, t: int,
                                velocidad_anterior: int, velocidad_nueva: int) -> int:
    """§2.3 — cambio de velocidad con acción ya programada."""
    restante = tiempo_siguiente - t
    restante_nuevo = max(1, restante * velocidad_anterior // velocidad_nueva)
    return t + restante_nuevo
