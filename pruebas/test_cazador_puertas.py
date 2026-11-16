"""US3 de la spec 003: puertas, invalidación de rutas y compartir la búsqueda (FR-015 a FR-018).

    uv run python -m unittest pruebas.test_cazador_puertas
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_cazador import armar_modelo, crear_enemigo, programar, sala, turno
from cripta.modelo.Puertas import abrir_salida, procesar_cierre_puerta


def _dos_caminos():
    # 1 -E-> 2 -E-> 3 (puerta de 2 a 3 cerrada); desvío 1 -S-> 4 -E-> 3 más caro
    return armar_modelo([
        sala(1, [["E", 2, {"costo": 100}], ["S", 4, {"costo": 150}]]),
        sala(2, [["E", 3, {"costo": 100, "cerrada": True}], ["O", 1, {"costo": 100}]]),
        sala(3, []),
        sala(4, [["E", 3, {"costo": 150}], ["N", 1, {"costo": 150}]])], 3)


class CazadorPuertasPruebas(unittest.TestCase):
    def test_usa_desvio_si_la_puerta_esta_cerrada(self):
        """FR-015: la puerta cerrada no se abre ni se atraviesa; toma el desvío abierto."""
        m = _dos_caminos()
        c = crear_enemigo(m, "cazador", "c-1", 1, rango=10 ** 6)
        programar(m, c, 0)
        turno(m, c)
        self.assertEqual(c.sala, 4)
        self.assertTrue(m.salas.obtener(2).salidas.obtener("E").cerrada)

    def test_abrir_puerta_invalida_y_cambia_la_ruta(self):
        """FR-017: al abrir una puerta se recalcula y se usa el camino nuevo más barato."""
        m = _dos_caminos()
        p = m.sim.persecucion
        s1 = m.salas.obtener(1).salidas
        self.assertEqual(p.decidir(3, 1, s1, 10 ** 6).sala_destino, 4)
        recalculos = p.recalculos
        self.assertEqual(p.decidir(3, 1, s1, 10 ** 6).sala_destino, 4)
        self.assertEqual(p.recalculos, recalculos)         # sin cambios: se reutiliza
        abrir_salida(m.salas.obtener(2).salidas.obtener("E"), 0, m.sim.agenda)
        self.assertEqual(p.decidir(3, 1, s1, 10 ** 6).sala_destino, 2)
        self.assertEqual(p.recalculos, recalculos + 1)

    def test_cierre_automatico_invalida(self):
        """FR-017: el cierre de una puerta también invalida las distancias."""
        m = _dos_caminos()
        puerta = m.salas.obtener(2).salidas.obtener("E")
        abrir_salida(puerta, 0, m.sim.agenda)
        p = m.sim.persecucion
        s1 = m.salas.obtener(1).salidas
        self.assertEqual(p.decidir(3, 1, s1, 10 ** 6).sala_destino, 2)
        procesar_cierre_puerta(puerta, m.sim.agenda)
        self.assertEqual(p.decidir(3, 1, s1, 10 ** 6).sala_destino, 4)

    def test_cambio_de_sala_del_jugador_invalida(self):
        """FR-017: si el jugador cambia de sala se busca de nuevo."""
        m = _dos_caminos()
        p = m.sim.persecucion
        s1 = m.salas.obtener(1).salidas
        p.decidir(3, 1, s1, 10 ** 6)
        r = p.recalculos
        p.decidir(4, 1, s1, 10 ** 6)
        self.assertEqual(p.recalculos, r + 1)

    def test_varios_cazadores_comparten_una_busqueda(self):
        """FR-016, FR-018: N cazadores en el mismo estado hacen una sola búsqueda; la muerte de otro actor no invalida."""
        m = armar_modelo([sala(1, [["E", 2, {}]]), sala(2, [["E", 3, {}], ["O", 1, {}]]),
                          sala(3, [["O", 2, {}]])], 3)
        cazadores = [crear_enemigo(m, "cazador", f"c-{i}", 1, rango=1000) for i in range(30)]
        p = m.sim.persecucion
        p.registrar_rango(1000)
        s1 = m.salas.obtener(1).salidas
        for c in cazadores:
            p.decidir(3, 1, s1, 1000)
        self.assertEqual(p.recalculos, 1)
        cazadores[0].vida = 0        # un actor muere: no cambia puertas ni rutas
        p.decidir(3, 1, s1, 1000)
        self.assertEqual(p.recalculos, 1)

    def test_rango_mayor_obliga_a_recalcular(self):
        """FR-025: si aparece un cazador con rango mayor que el usado, se amplía la búsqueda."""
        costos = [100] * 5
        descripcion = []
        for i in range(1, 7):
            salidas = []
            if i < 6:
                salidas.append(["E", i + 1, {"costo": 100}])
            if i > 1:
                salidas.append(["O", i - 1, {"costo": 100}])
            descripcion.append(sala(i, salidas))
        m = armar_modelo(descripcion, 6)
        p = m.sim.persecucion
        s1 = m.salas.obtener(1).salidas
        self.assertIsNone(p.decidir(6, 1, s1, 200))          # d = 500 > 200: espera
        self.assertIsNotNone(p.decidir(6, 1, s1, 600))       # rango mayor: busca más lejos
        self.assertEqual(p.recalculos, 2)


if __name__ == "__main__":
    unittest.main()
