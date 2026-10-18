"""El jugador muestra su equipo: clasificación de armas/armaduras y cuadros del sprite."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cripta.vista.grafica import heroe


class PruebasHeroe(unittest.TestCase):
    def test_clasifica_equipo_de_las_criptas(self):
        casos = [["itm_daga_oxidada Daga oxidada", "daga"], ["sl_hacha_campamento Hacha de campamento", "hacha"],
                 ["sl_lanza_puentes Lanza de los Puenteceros", "lanza"], ["sl_baston_fabrial Baston de fabrial", "baston"],
                 ["sl_hoja_esquirlada Hoja esquirlada", "espada"], ["", "ninguna"], ["Objeto raro", "espada"]]
        for texto, tipo in casos:
            self.assertEqual(heroe.tipo_arma(texto), tipo, texto)
        for texto, tipo in [["itm_coraza_cuero Coraza de cuero", "cuero"], ["sl_manto_explorador Manto", "manto"],
                            ["sl_armadura_esquirlada Armadura esquirlada", "placas"], ["", "ninguna"],
                            ["Pechera rara", "malla"]]:
            self.assertEqual(heroe.tipo_armadura(texto), tipo, texto)

    def test_spritesheets_exportados_contienen_todos_los_cuadros(self):
        import json
        from cripta.vista.grafica.assets import CARPETA, animaciones, imagen

        with (CARPETA / "animaciones.json").open(encoding="utf-8") as archivo:
            indice = json.load(archivo)
        self.assertEqual(len(indice), 76)
        for nombre, ancho, alto, cantidades in indice:
            hoja = imagen(nombre)
            self.assertEqual(list(hoja.size), [max(cantidades) * ancho, len(cantidades) * alto], nombre)
            grupos = animaciones(nombre)
            self.assertEqual([len(g) for g in grupos], cantidades, nombre)
            for grupo in grupos:
                for cuadro in grupo:
                    self.assertEqual(list(cuadro.size), [ancho, alto], nombre)
                    self.assertIsNotNone(cuadro.getbbox(), nombre)

    def test_animaciones_comparten_lienzo_y_el_equipo_cambia_el_dibujo(self):
        sin_nada = heroe.animaciones()
        equipado = heroe.animaciones("espada", "placas", True)
        self.assertEqual([len(a) for a in sin_nada], [4, 4, 6, 3, 3])
        for grupo in sin_nada + equipado:
            for cuadro in grupo:
                self.assertEqual(cuadro.size, (heroe.ANCHO, heroe.ALTO))
        self.assertNotEqual(sin_nada[0][0].tobytes(), equipado[0][0].tobytes())
        # Sin arma, el golpe es un puñetazo: el cuadro de impacto difiere del de reposo.
        self.assertNotEqual(sin_nada[2][3].tobytes(), sin_nada[0][0].tobytes())


if __name__ == "__main__":
    unittest.main()
