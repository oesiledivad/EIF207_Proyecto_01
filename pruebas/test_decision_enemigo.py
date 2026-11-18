"""Contrato de decisión de enemigo `[tipo, destino, costo]` (contracts/decision-enemigo.md).

    uv run python -m unittest pruebas.test_decision_enemigo
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_cazador import armar_modelo, crear_enemigo, sala


def _modelo():
    # sala 1: tres salidas abiertas (costos 10, 20, 30) y una cerrada; el jugador está en 9
    return armar_modelo([
        sala(1, [["N", 2, {"costo": 10}], ["S", 3, {"costo": 20}],
                 ["E", 4, {"costo": 30}], ["O", 5, {"costo": 40, "cerrada": True}]]),
        sala(2, []), sala(3, []), sala(4, []), sala(5, []), sala(9, []),
    ], 9)


class DecisionEnemigoPruebas(unittest.TestCase):
    def test_guardian_espera_sin_destino_ni_costo(self):
        """FR-003: el guardián devuelve esperar con destino y costo en nada."""
        m = _modelo()
        guardian = crear_enemigo(m, "guardian", "g-1", 1)
        self.assertEqual(guardian.decidir_accion(9, m.salas, 0, random.Random(1)),
                         ["esperar", None, None])

    def test_atacar_al_compartir_sala(self):
        """FR-010: al compartir sala se ataca, sin destino ni costo."""
        m = _modelo()
        for comportamiento in ["guardian", "errante", "rastreador", "cazador"]:
            enemigo = crear_enemigo(m, comportamiento, f"x-{comportamiento}", 1)
            self.assertEqual(enemigo.decidir_accion(1, m.salas, 0, random.Random(1), m.sim.persecucion),
                             ["atacar", None, None])

    def test_errante_mismo_destino_y_mismo_azar_que_antes(self):
        """FR-003, FR-022: el errante elige igual que `azar.choice` sobre los destinos abiertos y no cambia el azar."""
        for semilla in range(1, 30):
            m = _modelo()
            errante = crear_enemigo(m, "errante", "e-1", 1)
            azar = random.Random(semilla)
            tipo, destino, costo = errante.decidir_accion(9, m.salas, 0, azar)
            referencia = random.Random(semilla)
            destinos = [s.sala_destino for s in m.salas.obtener(1).salidas if not s.cerrada]
            esperado = referencia.choice(destinos)
            self.assertEqual([tipo, destino], ["mover", esperado])
            self.assertEqual(costo, m.salas.obtener(1).salidas.obtener(
                {2: "N", 3: "S", 4: "E"}[esperado]).costo)
            self.assertEqual(azar.getstate(), referencia.getstate())

    def test_errante_sin_salidas_abiertas_espera(self):
        """FR-003: sin salidas abiertas el errante espera y no toca el azar."""
        m = armar_modelo([sala(1, [["N", 2, {"cerrada": True}]]), sala(2, []), sala(9, [])], 9)
        errante = crear_enemigo(m, "errante", "e-1", 1)
        azar = random.Random(3)
        estado = azar.getstate()
        self.assertEqual(errante.decidir_accion(9, m.salas, 0, azar), ["esperar", None, None])
        self.assertEqual(azar.getstate(), estado)

    def test_rastreador_mismo_destino_con_el_costo_de_su_salida(self):
        """FR-003, FR-022: el rastreador elige la vecina de marca más fresca y devuelve el costo de esa salida."""
        m = _modelo()
        m.salas.obtener(2).ultimo_tiempo_visita = 100
        m.salas.obtener(4).ultimo_tiempo_visita = 300
        rastreador = crear_enemigo(m, "rastreador", "r-1", 1)
        self.assertEqual(rastreador.decidir_accion(9, m.salas, 350, random.Random(1)),
                         ["mover", 4, 30])
        self.assertEqual(rastreador.decidir_accion(9, m.salas, 900, random.Random(1)),
                         ["esperar", None, None])


if __name__ == "__main__":
    unittest.main()
