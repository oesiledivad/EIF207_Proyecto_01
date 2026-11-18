"""Pruebas de la cola propia ColaLista."""
import unittest

from cripta.estructuras.Cola_Lista import ColaLista


class PruebasColaLista(unittest.TestCase):
    def test_orden_fifo(self):
        """FR-024: los elementos salen en el orden en que entraron."""
        cola = ColaLista()
        for valor in (3, 1, 2):
            cola.encolar(valor)
        self.assertEqual([cola.sacar(), cola.sacar(), cola.sacar()], [3, 1, 2])

    def test_vacia(self):
        """FR-024: `vacia` refleja si quedan elementos."""
        cola = ColaLista()
        self.assertTrue(cola.vacia())
        cola.encolar("a")
        self.assertFalse(cola.vacia())
        cola.sacar()
        self.assertTrue(cola.vacia())

    def test_sacar_de_cola_vacia(self):
        """FR-024: sacar de una cola vacía es un error explícito."""
        with self.assertRaises(IndexError):
            ColaLista().sacar()

    def test_diez_mil_sin_pop_cero(self):
        """FR-024: tras 10 000 encolar y sacar no se usa `pop(0)`; avanza la cabeza."""
        cola = ColaLista()
        for i in range(10_000):
            cola.encolar(i)
        for i in range(10_000):
            self.assertEqual(cola.sacar(), i)
        self.assertTrue(cola.vacia())
        # Sin pop(0) los elementos no se desplazan: la cabeza recorrió todo.
        self.assertGreaterEqual(cola._cabeza, 10_000)


if __name__ == "__main__":
    unittest.main()
