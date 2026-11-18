"""Estructura LineaTiempo sin juego (spec 004, D2 a D8)."""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.estructuras.Linea_Tiempo import LineaTiempo


def _partida(k, acciones=60, semilla=5, ranuras=4):
    """Línea sintética y el estado verdadero antes de cada acción y tras cada cambio."""
    azar = random.Random(semilla)
    linea = LineaTiempo(k, [0] * ranuras)
    verdad = [0] * ranuras
    antes_de = []          # estado antes de cada acción
    t = 0
    for _ in range(acciones):
        antes_de.append(list(verdad))
        linea.marcar(t)
        instante = t
        for _ in range(azar.randrange(0, 4)):
            ranura = azar.randrange(ranuras)
            valor = azar.randrange(5)
            instante += azar.randrange(0, 2)          # varios cambios pueden compartir instante
            linea.registrar(instante, ranura, valor)
            verdad[ranura] = valor
            if azar.random() < 0.1:
                nueva = linea.nueva_ranura(9)
                verdad.append(9)
                linea.registrar(instante, nueva, 1)
                verdad[nueva] = 1
        t = instante + 1 + azar.randrange(3)
    return linea, verdad, antes_de


class TestLineaTiempo(unittest.TestCase):
    def test_registra_solo_cambios_reales(self):
        """FR-014: un valor igual al vigente no ocupa memoria."""
        linea = LineaTiempo(3, [1, 2])
        self.assertFalse(linea.registrar(0, 0, 1))
        self.assertTrue(linea.registrar(0, 0, 5))
        self.assertEqual(linea.cambios(), 1)
        with self.assertRaises(ValueError):
            LineaTiempo(0)

    def test_tres_modos_iguales(self):
        """FR-015 y FR-016: adelante, atrás y el más cercano dan el estado verdadero de cada acción."""
        for k in [1, 2, 5, 100]:
            linea, verdad, antes_de = _partida(k)
            for numero in range(1, linea.acciones() + 2):
                esperado = antes_de[numero - 1] if numero <= len(antes_de) else verdad
                pos, marca = linea.ubicar_accion(numero)
                for modo in ["adelante", "atras", "cercano"]:
                    obtenido = linea.estado_en(pos, marca, modo)
                    self.assertEqual(obtenido[:len(esperado)], esperado, f"K={k} #{numero} {modo}")
                    self.assertLessEqual(linea.acciones_recorridas(pos, marca, modo), k)

    def test_estado_por_tiempo(self):
        """FR-001: en el instante de una marca es el estado antes de decidir; entre marcas, lo ocurrido hasta t."""
        linea = LineaTiempo(2, [0])
        linea.marcar(0)
        linea.registrar(0, 0, 1)
        linea.registrar(5, 0, 2)
        linea.registrar(5, 0, 3)          # dos cambios en el mismo instante
        linea.marcar(10)
        linea.registrar(10, 0, 4)
        def en(t):
            pos, marca = linea.ubicar_tiempo(t)
            return linea.estado_en(pos, marca)[0]
        self.assertEqual([en(0), en(4), en(5), en(9), en(10), en(11)], [0, 1, 3, 3, 3, 4])

    def test_puntos_de_control_acotados(self):
        """FR-013: como máximo un punto de control cada K acciones."""
        for k in [1, 3, 10]:
            linea, _, _ = _partida(k, acciones=100)
            self.assertLessEqual(linea.puntos_de_control(), 100 // k + 1)

    def test_recorte(self):
        """FR-010 y FR-012: recortar devuelve el vector vivo al estado de la marca y quita puntos de control."""
        linea, _, antes_de = _partida(3, acciones=30)
        extra = linea.recortar(20)
        self.assertIsNone(extra)
        self.assertEqual(linea.acciones(), 19)
        self.assertEqual(linea._vivo[:len(antes_de[19])], antes_de[19])
        self.assertLessEqual(linea.puntos_de_control(), 18 // 3 + 1)
        self.assertEqual(linea.puntos_de_control(), 1 + 18 // 3)
        linea.marcar(10 ** 6, "nuevo")
        self.assertEqual(linea.recortar(20), "nuevo")
        with self.assertRaises(ValueError):
            linea.recortar(50)

    def test_con_k_y_datos(self):
        """FR-024 y FR-030: con otro K o tras serializar, la línea describe la misma partida."""
        linea, verdad, antes_de = _partida(4)
        for otra in [linea.con_k(1), linea.con_k(50), LineaTiempo.desde_datos(linea.a_datos())]:
            for numero in range(1, linea.acciones() + 2):
                pos, marca = otra.ubicar_accion(numero)
                pos0, marca0 = linea.ubicar_accion(numero)
                self.assertEqual(otra.estado_en(pos, marca), linea.estado_en(pos0, marca0))
        datos = linea.a_datos()
        datos[10] = datos[10][:1]           # puntos de control incoherentes
        datos[11] = datos[11][:1]
        with self.assertRaises(ValueError):
            LineaTiempo.desde_datos(datos)


if __name__ == "__main__":
    unittest.main()
