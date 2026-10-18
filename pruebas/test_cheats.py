"""Ayudas de prueba sin modificar las reglas ni contaminar registros normales."""
import tempfile
import unittest
from pathlib import Path

from cripta.controlador.Aplicacion import Aplicacion
from pruebas.test_replay import FuenteReplay
from cripta.modelo.Combate import aplicar_danio
from cripta.modelo.Efectos import aplicar_veneno


class PruebasCheats(unittest.TestCase):
    """Comprueba ayudas, marcado de sesión y vuelta a una partida normal."""

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.app = Aplicacion(FuenteReplay(), carpeta_logs=self.raiz)
        self.assertTrue(self.app.iniciar_partida("Jugador", "42", "cripta-01").ok)

    def test_ayudas_no_avanzan_el_tiempo_ni_el_azar(self):
        tiempo = self.app.estado_partida().reloj_virtual
        azar = self.app._simulacion.azar.getstate()
        self.app._jugador.vida = 1
        ataque = self.app._jugador.ataque
        defensa = self.app._jugador.defensa
        for nombre in ["curar", "ataque", "defensa"]:
            self.assertTrue(self.app.aplicar_truco(nombre).ok)
        estado = self.app.estado_partida()
        self.assertEqual(estado.jugador_vida, estado.jugador_vida_max)
        self.assertEqual(estado.jugador_ataque, ataque + 50)
        self.assertEqual(estado.jugador_defensa, defensa + 50)
        self.assertEqual(estado.reloj_virtual, tiempo)
        self.assertEqual(self.app._simulacion.azar.getstate(), azar)
        self.assertTrue(self.app.trucos_activos)

    def test_sesion_con_cheats_no_guarda_ni_registra_puntajes_o_replay(self):
        registro = self.app._partida.registro.ruta
        antes = registro.read_bytes()
        self.assertTrue(self.app.aplicar_truco("ataque").ok)
        self.assertFalse(self.app.guardar(self.raiz / "cheats.bin").ok)
        self.assertFalse((self.raiz / "cheats.bin").exists())
        self.assertTrue(self.app.esperar().ok)
        self.app.terminar()
        self.assertEqual(registro.read_bytes(), antes)
        self.assertEqual(self.app.puntajes(), [])

    def test_nueva_partida_vuelve_a_registrar_normalmente(self):
        self.assertTrue(self.app.aplicar_truco("defensa").ok)
        self.assertTrue(self.app.aplicar_truco("god_mode").ok)
        self.assertTrue(self.app.aplicar_truco("insta_kill").ok)
        self.assertTrue(self.app.iniciar_partida("Normal", "43", "cripta-01").ok)
        self.assertFalse(self.app.trucos_activos)
        self.assertFalse(self.app.truco_activo("god_mode"))
        self.assertFalse(self.app.truco_activo("insta_kill"))
        self.assertIsNotNone(self.app._partida.registro)
        self.assertTrue(self.app.guardar().ok)
        self.app.terminar()
        self.assertEqual(len(self.app.puntajes()), 1)
        self.assertEqual(self.app.puntajes()[0].nombre_jugador, "Normal")

    def test_truco_invalido_no_activa_el_modo(self):
        self.assertFalse(self.app.aplicar_truco("inexistente").ok)
        self.assertFalse(self.app.trucos_activos)
        self.app.terminar()
        self.assertFalse(self.app.aplicar_truco("curar").ok)

    def test_god_mode_bloquea_ataques_trampas_y_veneno(self):
        self.assertTrue(self.app.aplicar_truco("god_mode").ok)
        jugador = self.app._jugador
        aplicar_danio(jugador, 999999)
        aplicar_danio(jugador, 999999, self.app._simulacion.agenda)
        self.assertTrue(self.app.mover("N").ok)
        self.assertIsNotNone(jugador.evento_veneno)
        self.assertTrue(self.app.esperar().ok)
        self.assertEqual(jugador.vida, jugador.vida_max)
        self.assertTrue(self.app.estado_partida().activa)
        self.assertTrue(self.app.aplicar_truco("god_mode").ok)
        self.assertFalse(self.app.truco_activo("god_mode"))
        aplicar_danio(jugador, 7, self.app._simulacion.agenda)
        self.assertEqual(jugador.vida, jugador.vida_max - 7)
        self.assertTrue(self.app.trucos_activos)

    def test_insta_kill_usa_la_muerte_normal_y_cancela_eventos(self):
        self.assertTrue(self.app.mover("N").ok)
        enemigo = self.app._salas.obtener(2).enemigos[0]
        enemigo.vida = enemigo.vida_max = enemigo.defensa = 10000
        self.assertTrue(self.app.aplicar_truco("insta_kill").ok)
        derrotados = self.app.estado_partida().enemigos_derrotados
        self.assertTrue(self.app.atacar(enemigo.identificador).ok)
        self.assertEqual(enemigo.vida, 0)
        self.assertEqual(self.app.estado_partida().enemigos_derrotados, derrotados + 1)
        self.assertFalse(any(e.id == enemigo.identificador for e in self.app.estado_partida().enemigos))
        self.assertFalse(any(e.actor is enemigo for e in self.app._simulacion.agenda.eventos_validos()))
        self.assertTrue(self.app.aplicar_truco("insta_kill").ok)
        self.assertFalse(self.app.truco_activo("insta_kill"))
        self.assertTrue(self.app.trucos_activos)

    def test_antidoto_y_vida_maxima_no_consumen_tiempo(self):
        tiempo = self.app.estado_partida().reloj_virtual
        jugador = self.app._jugador
        aplicar_veneno(jugador, 10, tiempo, self.app._simulacion.agenda)
        evento = jugador.evento_veneno
        self.assertTrue(self.app.aplicar_truco("antidoto").ok)
        self.assertIsNone(jugador.evento_veneno)
        self.assertFalse(evento.valido)
        vida_maxima = jugador.vida_max
        self.assertTrue(self.app.aplicar_truco("vida").ok)
        self.assertEqual(jugador.vida_max, vida_maxima + 100)
        self.assertEqual(jugador.vida, jugador.vida_max)
        self.assertEqual(self.app.estado_partida().reloj_virtual, tiempo)
