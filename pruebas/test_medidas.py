"""Escalado del lienzo y fuente pixel: no requieren arcade."""
import unittest

from cripta.vista.grafica import fuente_pixel as fp
from cripta.vista.grafica.medidas import ALTO, ANCHO, calcular_escala, tamano_ventana_inicial


class PruebasMedidas(unittest.TestCase):
    def test_misma_proporcion_en_laptop_y_monitor(self):
        """La interfaz ocupa la misma fracción de la ventana en cualquier pantalla."""
        for ancho, alto in [[1366, 705], [1280, 720], [1536, 864], [1920, 1080], [2560, 1440], [640, 360]]:
            escala, ox, oy = calcular_escala(ancho, alto)
            self.assertLessEqual(ANCHO * escala + 2 * ox, ancho + 1)
            self.assertLessEqual(ALTO * escala + 2 * oy, alto + 1)
            self.assertGreaterEqual(ox, 0)
            self.assertGreaterEqual(oy, 0)
            # Se usa al menos el 90 % del lado que limita.
            self.assertGreaterEqual(max(ANCHO * escala / ancho, ALTO * escala / alto), 0.9)

    def test_escala_entera_cuando_casi_cabe(self):
        self.assertEqual(calcular_escala(1600, 900)[0], 2.0)
        self.assertEqual(calcular_escala(1700, 950)[0], 2.0)   # 2.11 -> 2 (pixel nítido)
        self.assertAlmostEqual(calcular_escala(1366, 705)[0], 705 / 450)

    def test_tamano_inicial_segun_pantalla(self):
        self.assertEqual(tamano_ventana_inicial(1920, 1080), [1600, 900])
        ancho, alto = tamano_ventana_inicial(1366, 768)        # laptop: no ocupa toda la pantalla
        self.assertLessEqual(ancho, 1366 * 0.9)
        self.assertLessEqual(alto, 768 * 0.85)
        self.assertAlmostEqual(ancho / alto, 16 / 9, delta=0.02)
        ancho, alto = tamano_ventana_inicial(1280, 720)        # 1920x1080 con escalado al 150 %
        self.assertLessEqual(alto, 720 * 0.85)

    def test_fuente_mide_y_envuelve(self):
        self.assertEqual(fp.ancho_texto(""), 0)
        self.assertEqual(fp.ancho_texto("A", 2), 10)
        self.assertGreater(fp.ancho_texto("ATACAR", 1, negrita=True), fp.ancho_texto("ATACAR"))
        mensaje = "Una puerta cerrada necesita la llave correcta para poder abrirse."
        lineas = fp.envolver(mensaje, 120)
        self.assertTrue(all(fp.ancho_texto(l) <= 120 for l in lineas))
        self.assertEqual(" ".join(lineas), mensaje)
        self.assertTrue(fp.recortar("Urithiru: ecos de la tormenta", 60).endswith("…"))
        for caracter in "áéíóúñÑ¿¡·—":
            self.assertNotEqual(fp.glifo(caracter), fp.glifo("?"))
