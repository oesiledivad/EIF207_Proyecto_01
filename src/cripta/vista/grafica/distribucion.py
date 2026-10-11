"""Posiciones visuales por sala, independientes del azar del juego."""
import math
import random


class Distribucion:
    """Conserva posiciones visuales por sala, separadas del estado del juego."""

    def __init__(self):
        """Prepara el registro de posiciones de la partida visible."""
        self.partida = None
        self.posiciones = []

    def preparar(self, estado):
        """Asigna celdas libres a entidades nuevas y conserva las existentes.

        Args:
            estado: Partida con la sala y sus enemigos y objetos visibles.
        """
        partida = [estado.cripta_id, estado.semilla]
        if partida != self.partida:
            self.partida = partida
            self.posiciones = []
        sala = estado.sala_actual_id
        entidades = [["enemigo", e.id] for e in estado.enemigos]
        entidades += [["objeto", o.id] for o in estado.objetos_suelo]
        existentes = [p for p in self.posiciones if p[0] == sala]
        nuevos = [e for e in entidades if not any(p[1:3] == e for p in existentes)]
        filas = max(4, math.ceil((len(existentes) + len(nuevos)) / 5))
        libres = [[col, fila] for fila in range(filas) for col in range(6)
                  if col != 2
                  and not any(p[3:] == [col, fila] for p in existentes)]
        # Este generador no consume el azar utilizado por la simulación.
        azar = random.Random(f"{estado.cripta_id}:{estado.semilla}:{sala}")
        for clase, id_ in nuevos:
            celda = libres.pop(azar.randrange(len(libres)))
            self.posiciones.append([sala, clase, id_, *celda])

    def filas(self, sala):
        """Devuelve la cantidad de filas necesaria para las posiciones de una sala."""
        return max(4, 1 + max((p[4] for p in self.posiciones if p[0] == sala), default=0))

    def posicion(self, sala, clase, id_, x, y, ancho, alto):
        """Convierte una celda registrada en coordenadas de la sala dibujada.

        Args:
            sala: Identificador de la sala.
            clase: Categoría visual, enemigo u objeto.
            id_: Identificador de la entidad.
            x: Origen horizontal del área de dibujo.
            y: Origen vertical del área de dibujo.
            ancho: Anchura del área de dibujo.
            alto: Altura del área de dibujo.

        Returns:
            list: Coordenadas [x, y] adaptadas al tamaño de la ventana.
        """
        p = next(p for p in self.posiciones if p[:3] == [sala, clase, id_])
        return [x + ancho * (0.12 + p[3] * 0.12),
                y + alto * (0.18 + p[4] * 0.56 / self.filas(sala))]
