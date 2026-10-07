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

    Returns:
        El evento de cierre programado, o None si la puerta no se cierra sola.
    """
    salida.cerrada = False
    salida.evento_cierre = None
    if salida.cierre_automatico is not None and salida.cierre_automatico > 0:
        salida.evento_cierre = agenda.insertar(
            tiempo_actual + salida.cierre_automatico, salida, "cierre_puerta"
        )
    return salida.evento_cierre


def revertir_apertura(salida, agenda) -> None:
    """Deshace una apertura: cancela el cierre pendiente (si hay) y vuelve a cerrar."""
    if salida.evento_cierre is not None:
        agenda.cancelar(salida.evento_cierre)
        salida.evento_cierre = None
    salida.cerrada = True


def procesar_cierre_puerta(salida) -> str:
    """Ejecuta el evento de cierre. Un actor al otro lado se queda allí (Apéndice B)."""
    salida.cerrada = True
    salida.evento_cierre = None
    return f"La puerta {salida.direccion} hacia la sala {salida.sala_destino} se cierra."