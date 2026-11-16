"""US2 de la spec 003: el cazador persigue al jugador (FR-011 a FR-014, FR-025).

    uv run python -m unittest pruebas.test_cazador
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_cazador import (armar_modelo, crear_enemigo, decision_desde_cero, programar,
                                   sala, turno)


def _linea(costos, rango, cazador_en, jugador_en):
    """Salas 1..n en línea; costos[i] une la sala i+1 con la i+2 en ambos sentidos."""
    n = len(costos) + 1
    descripcion = []
    for i in range(1, n + 1):
        salidas = []
        if i < n:
            salidas.append(["E", i + 1, {"costo": costos[i - 1]}])
        if i > 1:
            salidas.append(["O", i - 1, {"costo": costos[i - 2]}])
        descripcion.append(sala(i, salidas))
    m = armar_modelo(descripcion, jugador_en)
    c = crear_enemigo(m, "cazador", "c-1", cazador_en, rango=rango)
    programar(m, c, 0)
    return m, c


class CazadorPruebas(unittest.TestCase):
    def test_persigue_por_ruta_mas_barata(self):
        """FR-011: el cazador elige la ruta de menor costo total, no la de menos puertas."""
        # 1 -> 4 directo cuesta 500; 1 -> 2 -> 3 -> 4 cuesta 300
        m = armar_modelo([
            sala(1, [["E", 4, {"costo": 500}], ["S", 2, {"costo": 100}]]),
            sala(2, [["E", 3, {"costo": 100}]]), sala(3, [["E", 4, {"costo": 100}]]),
            sala(4, [])], 4)
        c = crear_enemigo(m, "cazador", "c-1", 1, rango=1000)
        programar(m, c, 0)
        turno(m, c)
        self.assertEqual(c.sala, 2)

    def test_dentro_y_fuera_de_rango(self):
        """FR-012, FR-013: persigue si d <= rango y espera si d > rango (frontera incluida)."""
        m, c = _linea([100, 100], 200, 1, 3)
        turno(m, c)
        self.assertEqual(c.sala, 2)                   # d = 200 = rango: persigue
        m, c = _linea([100, 100], 199, 1, 3)
        turno(m, c)
        self.assertEqual(c.sala, 1)                   # d = 200 > 199: espera
        self.assertEqual(c.tiempo_siguiente, 100)     # esperar cuesta 100

    def test_rango_cero_solo_ataca_en_la_misma_sala(self):
        """FR-012: con rango 0 nunca se mueve."""
        m, c = _linea([100], 0, 1, 2)
        turno(m, c)
        self.assertEqual(c.sala, 1)

    def test_empate_menor_id_y_luego_N_S_E_O(self):
        """FR-014: entre salidas de igual costo total gana el menor id de destino y luego N,S,E,O."""
        m = armar_modelo([
            sala(1, [["N", 7, {"costo": 100}], ["S", 5, {"costo": 100}], ["E", 6, {"costo": 100}]]),
            sala(5, [["E", 9, {"costo": 100}]]), sala(6, [["N", 9, {"costo": 100}]]),
            sala(7, [["O", 9, {"costo": 100}]]), sala(9, [])], 9)
        c = crear_enemigo(m, "cazador", "c-1", 1, rango=1000)
        programar(m, c, 0)
        turno(m, c)
        self.assertEqual(c.sala, 5)
        # mismo destino por dos salidas de igual costo: gana el orden N,S,E,O
        m = armar_modelo([
            sala(1, [["E", 2, {"costo": 100}], ["N", 2, {"costo": 100}]]), sala(2, [])], 2)
        c = crear_enemigo(m, "cazador", "c-1", 1, rango=1000)
        self.assertEqual(m.sim.persecucion.decidir(2, 1, m.salas.obtener(1).salidas, 1000).direccion, "N")

    def test_puerta_cerrada_no_cuenta_y_sin_ruta_espera(self):
        """FR-011, FR-013: una puerta cerrada no se atraviesa; sin ruta abierta espera."""
        m = armar_modelo([sala(1, [["E", 2, {"cerrada": True}]]), sala(2, [])], 2)
        c = crear_enemigo(m, "cazador", "c-1", 1, rango=10 ** 6)
        programar(m, c, 0)
        turno(m, c)
        self.assertEqual(c.sala, 1)

    def test_no_usa_azar(self):
        """FR-022: la decisión del cazador no consume el azar compartido."""
        m, c = _linea([100, 100], 500, 1, 3)
        antes = m.sim.azar.getstate()
        turno(m, c)
        self.assertEqual(m.sim.azar.getstate(), antes)

    def test_misma_sala_ataca(self):
        """FR-010: en la misma sala el cazador ataca y su siguiente turno es a 100/velocidad."""
        m, c = _linea([100], 500, 1, 1)
        vida = m.jugador.vida
        turno(m, c)
        self.assertLess(m.jugador.vida, vida)
        self.assertEqual(c.tiempo_siguiente, 100)

    def test_coincide_con_referencia_en_cuadriculas_aleatorias(self):
        """FR-011 a FR-014: la decisión de producción coincide con la referencia lenta."""
        for semilla in range(40):
            azar = random.Random(semilla)
            lado = 4
            descripcion = []
            for f in range(lado):
                for col in range(lado):
                    i = f * lado + col + 1
                    salidas = []
                    for dire, df, dc in (("N", -1, 0), ("S", 1, 0), ("E", 0, 1), ("O", 0, -1)):
                        nf, nc = f + df, col + dc
                        if 0 <= nf < lado and 0 <= nc < lado:
                            vecina = nf * lado + nc + 1
                            costo = 50 * (1 + (min(i, vecina) * 7 + max(i, vecina) * 3 + semilla) % 4)
                            salidas.append([dire, vecina, {"costo": costo,
                                                           "cerrada": azar.random() < 0.15}])
                    descripcion.append(sala(i, salidas))
            m = armar_modelo(descripcion, 1)
            destino_jugador = azar.randint(1, lado * lado)
            for rango in (0, 100, 300, 700, 5000):
                cazador = azar.randint(1, lado * lado)
                esperada = decision_desde_cero(m.salas, cazador, destino_jugador, rango)
                obtenida = m.sim.persecucion.decidir(destino_jugador, cazador,
                                                     m.salas.obtener(cazador).salidas, rango)
                self.assertEqual(None if esperada is None else esperada.clave,
                                 None if obtenida is None else obtenida.clave,
                                 f"semilla={semilla} rango={rango}")


if __name__ == "__main__":
    unittest.main()
