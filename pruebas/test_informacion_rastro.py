"""Información de huellas sin modificar el reloj ni descubrir salas."""
import unittest

from cripta.controlador.Aplicacion import Aplicacion
from cripta.modelo.enemigos.Rastreador import Rastreador
from pruebas.test_replay import FuenteReplay


class PruebasInformacionRastro(unittest.TestCase):
    def setUp(self):
        self.app = Aplicacion(FuenteReplay())
        self.assertTrue(self.app.iniciar_partida("Jugador", "42", "cripta-01").ok)

    def test_informa_limite_exacto_sin_revelar_salas_no_visitadas(self):
        app = self.app
        azar = app._simulacion.azar.getstate()
        self.assertTrue(any("Sala 1:" in linea for linea in app.estado_partida().rastro))
        lineas = app._exploracion.describir_rastro(399)
        self.assertTrue(any("rastreable 1 u.t. más" in linea for linea in lineas))
        self.assertFalse(any("Sala 2:" in linea for linea in lineas))
        lineas = app._exploracion.describir_rastro(400)
        self.assertTrue(any("rastro vencido" in linea for linea in lineas))
        self.assertEqual(app._simulacion.reloj.tiempo_actual, 0)
        self.assertEqual(app._simulacion.azar.getstate(), azar)
        self.assertEqual(app._salas.obtener(1).ultimo_tiempo_visita, 0)

    def test_movimiento_informa_marca_de_sala_abandonada(self):
        self.assertTrue(self.app.mover("N").ok)
        mensajes = [m.texto for m in self.app.bitacora().ultimos()]
        self.assertTrue(any("marca en sala 1 en t=0" in texto for texto in mensajes))
        self.assertTrue(any("Sala 2:" in linea for linea in self.app.estado_partida().rastro))

    def test_llegada_de_rastreador_informa_seguimiento_real(self):
        app = self.app
        enemigo = Rastreador("rastreador", 10, 10, 1, 0, 100, 2, 0)
        app._salas.obtener(2).agregar_enemigo(enemigo)
        app._simulacion.reloj.avanzar_hasta(399)
        mensajes = app._simulacion._ejecutar_turno_enemigo(enemigo, app._jugador, app._salas)
        self.assertEqual(enemigo.sala, 1)
        self.assertTrue(any("sigue tu rastro y entra en tu sala" in texto for texto in mensajes))

    def test_rastro_vencido_no_produce_aviso_de_seguimiento(self):
        app = self.app
        enemigo = Rastreador("rastreador", 10, 10, 1, 0, 100, 2, 0)
        app._salas.obtener(2).agregar_enemigo(enemigo)
        app._simulacion.reloj.avanzar_hasta(400)
        mensajes = app._simulacion._ejecutar_turno_enemigo(enemigo, app._jugador, app._salas)
        self.assertEqual(enemigo.sala, 2)
        self.assertEqual(mensajes, [])


if __name__ == "__main__":
    unittest.main()
