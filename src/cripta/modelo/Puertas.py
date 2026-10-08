"""Puertas: abrir con llave y cierre automático (§2.5, §2.10).

Una salida abierta se queda abierta, salvo que declare `cierre_automatico`:
entonces se programa un evento "cierre_puerta" en la agenda. El "actor" del
evento es la propia SalidaSimple, así que no hace falta una clase nueva.
"""

from __future__ import annotations


def buscar_llave(items: list, id_llave: str | None):
    """Devuelve el item del inventario cuya ficha coincide con la llave de la puerta.

    La llave no se consume (§2.5). O(n), n = tamaño del inventario (pequeño).
    """
    if not id_llave:
        return None
    for item in items:
        if item.tipo_id == id_llave:
            return item
    return None
def abrir_salida(salida, tiempo_actual: int, agenda):
    """Abre la salida y, si tiene cierre automático, programa su cierre.

    Usa agenda.cambiar para que el retroceso (P3) pueda deshacerlo solo.
    """
    agenda.cambiar(salida, "cerrada", False)
    agenda.cambiar(salida, "evento_cierre", None)
    if salida.cierre_automatico is not None and salida.cierre_automatico > 0:
        evento = agenda.insertar(
            tiempo_actual + salida.cierre_automatico, salida, "cierre_puerta"
        )
        agenda.cambiar(salida, "evento_cierre", evento)
    return salida.evento_cierre


def procesar_cierre_puerta(salida, agenda) -> str:
    """Ejecuta el evento de cierre. Un actor al otro lado se queda allí (Apéndice B)."""
    agenda.cambiar(salida, "cerrada", True)
    agenda.cambiar(salida, "evento_cierre", None)
    return f"La puerta {salida.direccion} hacia la sala {salida.sala_destino} se cierra."