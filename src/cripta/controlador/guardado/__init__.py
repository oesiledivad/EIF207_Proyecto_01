"""Guardado y carga binaria de la partida (extra de P1, §4.10).

Paquete con una responsabilidad por módulo:
    formato.py       constantes del formato (id global, versión de cuerpo, clases de actor)
    datos.py         estructuras intermedias entre los bytes y el modelo del juego
    escritura.py     modelo del juego -> bytes -> archivo
    lectura.py       archivo -> bytes -> estructuras intermedias (valida sin tocar la partida)
    restauracion.py  estructuras intermedias -> modelo del juego

El contenedor del archivo es estructuras/Guardado_Binario.py (header + índice por sala
+ cuerpos) y los campos se codifican con estructuras/Serializacion_Binaria.py (struct).

Una partida cargada no puede retroceder más allá del punto de carga (el historial
de deltas no se guarda) ni se graba en el registro de replay (no parte de t=0).

Complejidad:
    guardar: O(S + E) con S = salas y E = eventos válidos de la agenda
    cargar: O(S + E log E) (los eventos se reinsertan en orden)
"""

from cripta.controlador.guardado.Escritura import escribir_partida
from cripta.controlador.guardado.Lectura import leer_partida
from cripta.controlador.guardado.Restauracion import restaurar_partida

__all__ = ["escribir_partida", "leer_partida", "restaurar_partida"]