"""El azar visual no cambia el juego ni recoloca entidades al redibujar."""
import random
import unittest
from types import SimpleNamespace

from cripta.vista.grafica.distribucion import Distribucion


class PruebasDistribucion(unittest.TestCase):
    def test_posiciones_estables_unicas_y_azar_independiente(self):
        estado = SimpleNamespace(cripta_id="cripta", semilla=42, sala_actual_id=1,
                                 enemigos=[SimpleNamespace(id=str(i)) for i in range(12)],
                                 objetos_suelo=[SimpleNamespace(id=str(i)) for i in range(20)])
        azar = random.getstate()
        distribucion = Distribucion()
        distribucion.preparar(estado)
        posiciones = [list(p) for p in distribucion.posiciones]
        self.assertEqual(random.getstate(), azar)
        self.assertEqual(len(posiciones), 32)
        for i, posicion in enumerate(posiciones):
            self.assertNotEqual(posicion[3], 2)
            self.assertFalse(any(p[3:] == posicion[3:] for p in posiciones[:i]))
            for ancho, alto in [[410, 265], [800, 525]]:
                x, y = distribucion.posicion(1, posicion[1], posicion[2], 20, 155, ancho, alto)
                self.assertTrue(20 < x < 20 + ancho - 24)
                self.assertTrue(155 < y < 155 + alto - 24)
        estado.enemigos.pop()
        estado.sala_actual_id = 2
        distribucion.preparar(estado)
        estado.sala_actual_id = 1
        distribucion.preparar(estado)
        self.assertEqual(distribucion.posiciones[:32], posiciones)
        otra = Distribucion()
        estado.enemigos.append(SimpleNamespace(id="11"))
        otra.preparar(estado)
        self.assertEqual(otra.posiciones, posiciones)
        estado.semilla = 43
        otra.preparar(estado)
        self.assertNotEqual(otra.posiciones, posiciones)
