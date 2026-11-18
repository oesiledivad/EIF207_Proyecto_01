"""MonticuloMinimo: cola de prioridad propia con listas paralelas."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.estructuras.Monticulo_Minimo import MonticuloMinimo


class PruebasMonticuloMinimo(unittest.TestCase):
    def test_extrae_por_menor_prioridad(self):
        """FR-024: se extrae primero la menor prioridad."""
        m = MonticuloMinimo()
        for prioridad, elemento in [[5, "e"], [1, "a"], [3, "c"], [2, "b"]]:
            m.insertar(prioridad, 0, elemento)
        self.assertEqual([m.extraer_minimo()[2] for _ in range(4)], ["a", "b", "c", "e"])

    def test_empate_por_desempate_entero(self):
        """FR-024: con igual prioridad gana el menor desempate."""
        m = MonticuloMinimo()
        m.insertar(10, 7, "siete")
        m.insertar(10, 2, "dos")
        m.insertar(10, 5, "cinco")
        m.insertar(9, 99, "primero")
        self.assertEqual([m.extraer_minimo()[2] for _ in range(4)],
                         ["primero", "dos", "cinco", "siete"])

    def test_esta_vacio(self):
        """FR-024: esta_vacio refleja el contenido."""
        m = MonticuloMinimo()
        self.assertTrue(m.esta_vacio())
        m.insertar(1, 1, "x")
        self.assertFalse(m.esta_vacio())
        m.extraer_minimo()
        self.assertTrue(m.esta_vacio())

    def test_vaciar_deja_listo_para_otra_busqueda(self):
        """FR-038: vaciar reutiliza el montículo sin reasignar las listas."""
        m = MonticuloMinimo()
        for i in range(20):
            m.insertar(i, i, i)
        prioridad, elemento = m._prioridad, m._elemento
        m.vaciar()
        self.assertTrue(m.esta_vacio())
        self.assertTrue(m._prioridad is prioridad and m._elemento is elemento)
        m.insertar(4, 0, "nuevo")
        self.assertEqual(m.extraer_minimo()[2], "nuevo")

    def test_eliminacion_perezosa(self):
        """FR-038: el llamador reinserta con mejor prioridad y descarta la obsoleta."""
        m = MonticuloMinimo()
        vigente = [9, 9]
        m.insertar(9, 0, 0)
        m.insertar(9, 1, 1)
        vigente[1] = 3
        m.insertar(3, 1, 1)
        salida = []
        while not m.esta_vacio():
            prioridad, _, elemento = m.extraer_minimo()
            if prioridad > vigente[elemento]:
                continue
            salida.append([prioridad, elemento])
        self.assertEqual(salida, [[3, 1], [9, 0]])

    def test_diez_mil_inserciones_y_extracciones_en_orden(self):
        """FR-024 y FR-038: 10 000 elementos salen ordenados."""
        m = MonticuloMinimo()
        n = 10000
        for i in range(n):
            m.insertar((i * 7919) % n, i, i)
        anterior = -1
        for _ in range(n):
            prioridad, _, _ = m.extraer_minimo()
            self.assertGreaterEqual(prioridad, anterior)
            anterior = prioridad
        self.assertTrue(m.esta_vacio())


if __name__ == "__main__":
    unittest.main()
