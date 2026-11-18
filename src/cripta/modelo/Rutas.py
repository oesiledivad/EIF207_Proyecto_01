"""Rutas de menor costo sobre un subgrafo que decide el llamador (Parte II, §3.4).

`BuscadorRutas` corre un Dijkstra inverso desde el destino sobre las salidas
entrantes de cada sala, de modo que una sola búsqueda sirve a cualquier origen.
Qué salidas existen para la búsqueda lo decide el predicado `usable` del
llamador: «ir a» le pasa lo que el jugador conoce y la spec 003 podrá pasarle
otra cosa (D9). El módulo no conoce HTTP, archivos ni vista.

Se eligió un montículo propio (`MonticuloMinimo`, sin `heapq`) con eliminación
perezosa: al mejorar una distancia se reinserta y las entradas viejas se
descartan al extraerlas. Las listas `distancia` y `marca` se reutilizan entre
búsquedas: `marca[v] == generacion` indica que `distancia[v]` es de la búsqueda
actual, así no se reinicializan S posiciones en cada paso.

Complejidad (A aristas relajadas, V salas alcanzadas):
    distancias_hacia: O((V + A) log V), y se detiene al fijar `parar_en` o al superar `limite`
    (con corte por costo solo se visita la región alcanzable dentro del límite: O((V_R + A_R) log V_R))
    elegir_paso: O(4)
    distancia_de: O(1)
"""

from __future__ import annotations

from cripta.estructuras.Monticulo_Minimo import MonticuloMinimo
from cripta.estructuras.Salidas import indice_direccion


class BuscadorRutas:
    """Distancias mínimas hacia un destino y elección del primer paso.

    Args:
        tamano: Cantidad de salas S (los ids van de 0 a S - 1).
    """

    def __init__(self, tamano: int) -> None:
        self.distancia: list[int] = [0] * tamano
        self.marca: list[int] = [0] * tamano
        self.generacion = 0
        self.monticulo = MonticuloMinimo()

    def distancia_de(self, sala: int) -> int | None:
        """Distancia de la búsqueda actual, o nada si la sala no se alcanzó. O(1)."""
        if 0 <= sala < len(self.marca) and self.marca[sala] == self.generacion:
            return self.distancia[sala]
        return None

    def distancias_hacia(self, destino: int, entrantes: list, usable, parar_en: int | None = None,
                         limite: int | None = None) -> None:
        """Llena `distancia` desde `destino` recorriendo las salidas al revés.

        Args:
            destino: Sala a la que se quiere llegar.
            entrantes: Lista por id de sala con las salidas que llegan a ella.
            usable: Predicado que dice si una salida entra en la búsqueda.
            parar_en: Sala cuya distancia basta conocer; la búsqueda termina al
                fijarla (puede ser nada para llenar todo lo alcanzable).
            limite: Costo máximo de interés (FR-025). La búsqueda termina al extraer una
                entrada vigente con prioridad mayor que `limite`: toda sala con distancia real
                menor o igual que `limite` queda con su distancia exacta, y cualquier otra da
                nada o un valor mayor que `limite`. Con nada, la búsqueda es la de siempre
                («ir a» no cambia).
        """
        self.generacion += 1
        self.monticulo.vaciar()
        if not 0 <= destino < len(self.marca):
            return
        self.marca[destino] = self.generacion
        self.distancia[destino] = 0
        self.monticulo.insertar(0, destino, destino)
        while not self.monticulo.esta_vacio():
            prioridad, _, sala = self.monticulo.extraer_minimo()
            if prioridad != self.distancia[sala]:
                continue   # entrada obsoleta: la sala ya se fijó con una distancia menor
            if limite is not None and prioridad > limite:
                return   # el resto de la región queda fuera del costo de interés
            if sala == parar_en:
                return
            for salida in entrantes[sala]:
                if not usable(salida):
                    continue
                origen = salida.clave // 4
                candidata = prioridad + salida.costo
                if self.marca[origen] != self.generacion or candidata < self.distancia[origen]:
                    self.marca[origen] = self.generacion
                    self.distancia[origen] = candidata
                    self.monticulo.insertar(candidata, origen, origen)

    def elegir_paso(self, origen: int, salidas, usable):
        """La salida de `origen` que minimiza `costo + distancia[destino]`, o nada.

        Empata por menor id de sala destino y luego por el orden N, S, E, O.
        Debe llamarse tras `distancias_hacia` con el mismo predicado.
        """
        mejor = None
        mejor_total = mejor_destino = mejor_indice = 0
        for salida in salidas:
            destino = salida.sala_destino
            if destino == origen or not usable(salida) or self.distancia_de(destino) is None:
                continue
            total = salida.costo + self.distancia[destino]
            indice = indice_direccion(salida.direccion)
            if (mejor is None or total < mejor_total
                    or (total == mejor_total and (destino < mejor_destino
                        or (destino == mejor_destino and indice < mejor_indice)))):
                mejor, mejor_total, mejor_destino, mejor_indice = salida, total, destino, indice
        return mejor
