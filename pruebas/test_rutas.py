"""Buscador de rutas de menor costo sobre el conocimiento del jugador (US3)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import armar_aplicacion, sala
from cripta.estructuras.Salidas import Salidas, SalidaSimple, indice_direccion
from cripta.modelo.Rutas import BuscadorRutas


def _grafo(aristas, n):
    """Aristas `[origen, direccion, destino, costo o None]` a listas de salidas y entrantes."""
    salidas = [[] for _ in range(n)]
    entrantes = [[] for _ in range(n)]
    for origen, direccion, destino, costo in aristas:
        salida = SalidaSimple(direccion, destino, False)
        if costo is not None:
            salida.costo = costo
        salida.clave = origen * 4 + indice_direccion(direccion)
        salidas[origen].append(salida)
        entrantes[destino].append(salida)
    return salidas, entrantes


def _siempre(salida):
    return True


class PruebasRutas(unittest.TestCase):
    def test_us3_2_menor_costo_no_menos_saltos(self):
        """FR-023: se sigue la ruta de menor costo total aunque tenga más salas."""
        salidas, entrantes = _grafo([[1, "N", 9, 500], [1, "E", 2, 100], [2, "E", 9, 100]], 10)
        buscador = BuscadorRutas(10)
        buscador.distancias_hacia(9, entrantes, _siempre, 1)
        self.assertEqual(buscador.distancia_de(1), 200)
        self.assertEqual(buscador.elegir_paso(1, salidas[1], _siempre).direccion, "E")

    def test_us3_3_empate_menor_id(self):
        """FR-024: el empate va a la vecina de menor id; a igual sala, menor costo y luego N, S, E, O."""
        salidas, entrantes = _grafo([[1, "N", 3, 50], [1, "S", 2, 50],
                                     [2, "E", 9, 50], [3, "E", 9, 50]], 10)
        buscador = BuscadorRutas(10)
        buscador.distancias_hacia(9, entrantes, _siempre, 1)
        self.assertEqual(buscador.elegir_paso(1, salidas[1], _siempre).sala_destino, 2)
        # dos salidas hacia la misma sala: gana la de menor costo
        salidas, entrantes = _grafo([[1, "N", 2, 60], [1, "E", 2, 40], [2, "N", 9, 10]], 10)
        buscador.distancias_hacia(9, entrantes, _siempre, 1)
        self.assertEqual(buscador.elegir_paso(1, salidas[1], _siempre).direccion, "E")
        # a igual costo, el orden N, S, E, O (la E se declara primero)
        salidas, entrantes = _grafo([[1, "E", 2, 40], [1, "O", 2, 40], [1, "S", 2, 40],
                                     [1, "N", 2, 40], [2, "N", 9, 10]], 10)
        buscador.distancias_hacia(9, entrantes, _siempre, 1)
        self.assertEqual(buscador.elegir_paso(1, salidas[1], _siempre).direccion, "N")

    def test_us3_5_costo_por_defecto_100(self):
        """FR-023: una salida sin costo declarado cuenta 100."""
        salidas = Salidas()
        salidas.agregar("N", 2, False)
        self.assertEqual(next(iter(salidas)).costo, 100)
        salidas, entrantes = _grafo([[1, "N", 2, None], [2, "N", 3, None]], 4)
        buscador = BuscadorRutas(4)
        buscador.distancias_hacia(3, entrantes, _siempre, None)
        self.assertEqual(buscador.distancia_de(1), 200)
        self.assertEqual(buscador.distancia_de(3), 0)

    def test_marca_de_generacion_no_arrastra_distancias(self):
        """FR-022: reutilizar el buscador no deja distancias de la búsqueda anterior."""
        salidas, entrantes = _grafo([[1, "N", 2, 10], [2, "N", 3, 10]], 4)
        buscador = BuscadorRutas(4)
        buscador.distancias_hacia(3, entrantes, _siempre, None)
        self.assertEqual(buscador.distancia_de(1), 20)
        buscador.distancias_hacia(2, entrantes, _siempre, None)
        self.assertEqual(buscador.distancia_de(1), 10)
        self.assertIsNone(buscador.distancia_de(3))   # tenía 0 en la búsqueda anterior
        self.assertIsNone(buscador.elegir_paso(3, salidas[3], _siempre))
        self.assertIsNone(buscador.distancia_de(99))

    def test_solo_exploradas_y_abiertas(self):
        """FR-022 y FR-023: solo salas exploradas y salidas con puerta recordada abierta."""
        esqueleto = [
            sala(1, [["N", 2], ["E", 3, {"cerrada": True, "llave": "k"}]]),
            sala(2, [["S", 1], ["N", 4]]),
            sala(3, [["O", 1], ["E", 5]]),
            sala(4, [["S", 2]]),
            sala(5, [["O", 3]]),
        ]
        app = armar_aplicacion(esqueleto, sala_inicial=1, sala_salida=4)
        c = app._exploracion.conocimiento
        entrantes = app._exploracion.entrantes
        salas = app._salas
        norte, este = salas.obtener(1).salidas.obtener("N"), salas.obtener(1).salidas.obtener("E")
        self.assertFalse(c.salida_usable(norte))      # el destino solo está avistado
        self.assertTrue(app.mover("N").ok)
        self.assertTrue(c.salida_usable(norte))
        self.assertTrue(c.salida_usable(salas.obtener(2).salidas.obtener("S")))
        self.assertFalse(c.salida_usable(salas.obtener(2).salidas.obtener("N")))  # destino avistado
        c.explorar(3, app._gestor.historial, 0)
        self.assertFalse(c.salida_usable(este))       # puerta recordada cerrada
        c.explorar(5, app._gestor.historial, 0)
        self.assertFalse(c.salida_usable(salas.obtener(3).salidas.obtener("E")))  # sin observar
        self.assertFalse(c.salida_usable(salas.obtener(5).salidas.obtener("O")))  # sin observar
        c.explorar(4, app._gestor.historial, 0)
        self.assertTrue(c.salida_usable(salas.obtener(2).salidas.obtener("N")))
        buscador = BuscadorRutas(len(c.estado_sala))
        buscador.distancias_hacia(4, entrantes, c.salida_usable, 1)
        self.assertEqual(buscador.elegir_paso(1, salas.obtener(1).salidas, c.salida_usable).direccion, "N")
        buscador.distancias_hacia(3, entrantes, c.salida_usable, 1)
        self.assertIsNone(buscador.elegir_paso(1, salas.obtener(1).salidas, c.salida_usable))
        buscador.distancias_hacia(3, entrantes, c.salida_usable, 5)
        self.assertIsNone(buscador.elegir_paso(5, salas.obtener(5).salidas, c.salida_usable))


if __name__ == "__main__":
    unittest.main()
