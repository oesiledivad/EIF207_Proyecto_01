"""US1 de la spec 003: moverse consume el costo de la salida (FR-001 a FR-007).

    uv run python -m unittest pruebas.test_costo_movimiento
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_cazador import armar_modelo, crear_enemigo, programar, sala, turno
from pruebas.apoyo_niebla import armar_aplicacion
from cripta.util.Costo_Acciones import calcular_intervalo, costo_accion


def _app(salidas_sala_1, velocidad=100):
    """Aplicación con la sala 1 de salidas dadas, salas destino enlazadas de vuelta y jugador a `velocidad`."""
    salas = [sala(1, salidas_sala_1),
             sala(2, [["O", 1, {"costo": 70}]]),
             sala(3, [["S", 1, {"costo": 100}]])]
    app = armar_aplicacion(salas)
    app._jugador.velocidad = velocidad
    return app


class CostoMovimientoPruebas(unittest.TestCase):
    def test_us1_1_sin_costo_vale_100(self):
        """FR-001, FR-003, FR-004: sin costo declarado la salida vale 100 y el turno llega 100 después."""
        app = _app([["E", 2, {}]])
        t0 = app._simulacion.reloj.tiempo_actual
        self.assertTrue(app.mover("E").ok)
        self.assertEqual(app._simulacion.reloj.tiempo_actual, t0 + 100)

    def test_us1_2_costo_250(self):
        """FR-003, FR-004: con una salida de costo 250 y velocidad 100 el siguiente turno es 250 después."""
        app = _app([["E", 2, {"costo": 250}]])
        t0 = app._simulacion.reloj.tiempo_actual
        self.assertTrue(app.mover("E").ok)
        self.assertEqual(app._simulacion.reloj.tiempo_actual, t0 + 250)

    def test_apendice_b_6_velocidad_alta_costo_1(self):
        """FR-004: Apéndice B, caso 6. Con velocidad alta y costo 1 el intervalo es 1, nunca 0."""
        app = _app([["E", 2, {"costo": 1}]], velocidad=1000)
        t0 = app._simulacion.reloj.tiempo_actual
        self.assertTrue(app.mover("E").ok)
        self.assertEqual(app._simulacion.reloj.tiempo_actual, t0 + 1)
        self.assertEqual(calcular_intervalo(1, 1000), 1)
        # un enemigo errante de velocidad 1000 por una salida de costo 1
        m = armar_modelo([sala(1, [["E", 2, {"costo": 1}]]), sala(2, []), sala(9, [])], 9)
        errante = crear_enemigo(m, "errante", "e-1", 1, velocidad=1000)
        programar(m, errante, 10)
        turno(m, errante)
        self.assertEqual(errante.sala, 2)
        self.assertEqual(errante.tiempo_siguiente, 11)

    def test_apendice_b_7_cambio_velocidad_con_movimiento_costoso(self):
        """FR-006: Apéndice B, caso 7. El tiempo restante se reescala según P1 §2.3."""
        m = armar_modelo([sala(1, [["E", 2, {"costo": 300}]]), sala(2, [])], 1)
        # jugador: salida de costo 300, velocidad 100, turno pendiente en t + 300
        jugador = m.jugador
        evento = m.sim.agenda.insertar(300, jugador, "accion_actor")
        jugador._proximo_evento = evento
        jugador.tiempo_siguiente = 300
        m.sim.reloj.avanzar_hasta(150)    # a mitad del intervalo
        jugador.actualizar_velocidad(200, 150, m.sim.agenda)
        self.assertEqual(jugador.tiempo_siguiente, 150 + max(1, 150 * 100 // 200))
        # cambio a velocidad 1: el restante se multiplica por 100
        m.sim.reloj.avanzar_hasta(160)
        jugador.actualizar_velocidad(1, 160, m.sim.agenda)
        self.assertEqual(jugador.tiempo_siguiente, 160 + max(1, (225 - 160) * 200 // 1))
        # un enemigo que acaba de moverse por una salida costosa
        m2 = armar_modelo([sala(1, [["E", 2, {"costo": 300}]]), sala(2, []), sala(9, [])], 9)
        errante = crear_enemigo(m2, "errante", "e-1", 1, velocidad=100)
        programar(m2, errante, 0)
        turno(m2, errante)
        self.assertEqual(errante.tiempo_siguiente, 300)
        m2.sim.reloj.avanzar_hasta(100)
        errante.actualizar_velocidad(300, 100, m2.sim.agenda)
        self.assertEqual(errante.tiempo_siguiente, 100 + max(1, 200 * 100 // 300))

    def test_us1_5_otras_acciones_no_cambian(self):
        """FR-005: esperar, atacar, usar y abrir una puerta cuestan lo mismo que en la Parte I."""
        app = _app([["E", 2, {"costo": 1}], ["N", 3, {"costo": 250}]])
        self.assertEqual(costo_accion("atacar"), 100)
        self.assertEqual(costo_accion("usar_objeto"), 50)
        self.assertEqual(costo_accion("abrir_puerta"), 50)
        t0 = app._simulacion.reloj.tiempo_actual
        self.assertTrue(app.esperar().ok)
        self.assertEqual(app._simulacion.reloj.tiempo_actual, t0 + 100)

    def test_us1_6_mismo_costo_en_ambos_sentidos(self):
        """FR-001: una conexión de costo 70 cuesta 70 de A a B y de B a A."""
        app = _app([["E", 2, {"costo": 70}]])
        t0 = app._simulacion.reloj.tiempo_actual
        self.assertTrue(app.mover("E").ok)
        self.assertEqual(app._simulacion.reloj.tiempo_actual, t0 + 70)
        self.assertTrue(app.mover("O").ok)
        self.assertEqual(app._simulacion.reloj.tiempo_actual, t0 + 140)

    def test_us1_7_enemigos_pagan_el_costo(self):
        """FR-003, FR-004: un errante y un rastreador reprograman su turno a t + max(1, costo*100//velocidad)."""
        esperado = max(1, 180 * 100 // 120)
        m = armar_modelo([sala(1, [["E", 2, {"costo": 180}]]), sala(2, []), sala(9, [])], 9)
        errante = crear_enemigo(m, "errante", "e-1", 1, velocidad=120)
        programar(m, errante, 50)
        turno(m, errante)
        self.assertEqual(errante.sala, 2)
        self.assertEqual(errante.tiempo_siguiente, 50 + esperado)
        # rastreador: la sala vecina tiene una marca fresca
        m = armar_modelo([sala(1, [["E", 2, {"costo": 180}]]), sala(2, []), sala(9, [])], 9)
        m.salas.obtener(2).ultimo_tiempo_visita = 40
        rastreador = crear_enemigo(m, "rastreador", "r-1", 1, velocidad=120)
        programar(m, rastreador, 50)
        turno(m, rastreador)
        self.assertEqual(rastreador.sala, 2)
        self.assertEqual(rastreador.tiempo_siguiente, 50 + esperado)

    def test_ir_a_consume_costo_de_cada_paso(self):
        """FR-007: un viaje de «ir a» por salidas de costo 40 y 160 avanza el reloj 40 y luego 160."""
        salas = [sala(1, [["E", 2, {"costo": 40}]]),
                 sala(2, [["O", 1, {"costo": 40}], ["E", 3, {"costo": 160}]]),
                 sala(3, [["O", 2, {"costo": 160}]])]
        app = armar_aplicacion(salas)
        app._jugador.velocidad = 100
        self.assertTrue(app.mover("E").ok)
        self.assertTrue(app.mover("E").ok)
        t = app._simulacion.reloj.tiempo_actual
        self.assertEqual(t, 200)
        resultado = app.ir_a_completo(1)
        self.assertTrue(resultado.ok)
        self.assertEqual(app._jugador.sala, 1)
        self.assertEqual(app._simulacion.reloj.tiempo_actual, t + 160 + 40)


if __name__ == "__main__":
    unittest.main()
