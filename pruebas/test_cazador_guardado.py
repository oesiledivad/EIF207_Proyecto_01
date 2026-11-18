"""US5 de la spec 003: coherencia con replay, guardado y retroceso (FR-022 a FR-024).

    uv run python -m unittest pruebas.test_cazador_guardado
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_cazador import (FuenteCazador, armar_aplicacion_cazador, decision_desde_cero,
                                   enemigos_en, ficha_enemigo, sala)
from cripta.controlador.guardado.Escritura import _escribir_enemigo
from cripta.controlador.guardado.Formato import VERSION_CUERPO
from cripta.controlador.guardado.Lectura import _leer_enemigo
from cripta.estructuras.serializacionBinaria.EscritorBinario import EscritorBinario
from cripta.estructuras.serializacionBinaria.LectorBinario import LectorBinario
from cripta.replay.reproductor import reproducir

CAZADOR = "cazador-x"


def _esqueleto():
    """1 -300- 2 -100- 3 -100- 4 en línea; el cazador empieza en la sala 2."""
    return [sala(1, [["E", 2, {"costo": 300}]]),
            sala(2, [["O", 1, {"costo": 300}], ["E", 3, {"costo": 100}]]),
            sala(3, [["O", 2, {"costo": 100}], ["E", 4, {"costo": 100}]]),
            sala(4, [["O", 3, {"costo": 100}]])]


def _contenidos(con_pergamino=False):
    primera = {"sala": 1, "enemigos": [], "trampas": [],
               "objetos": ["itm_pergamino_retroceso"] if con_pergamino else []}
    return [primera, enemigos_en(2, [["c1", CAZADOR]])]


def _fichas(ataque=1):
    return [ficha_enemigo(CAZADOR, rango=1000, velocidad=100, vida_max=500, ataque=ataque)]


def _app(ruta_guardado=None, carpeta_logs=None, con_pergamino=False):
    return armar_aplicacion_cazador(_esqueleto(), _fichas(), _contenidos(con_pergamino),
                                    sala_inicial=1, sala_salida=4,
                                    ruta_guardado=ruta_guardado, carpeta_logs=carpeta_logs)


def _cazador(app):
    for s in app._salas._datos:
        if s is not None:
            for e in s.enemigos:
                if e.comportamiento == "cazador":
                    return e
    raise AssertionError("no hay cazador")


def _firma(app):
    sim = app._simulacion
    c = _cazador(app)
    return [sim.reloj.tiempo_actual, sim.azar.getstate(), app._jugador.sala, app._jugador.vida,
            c.sala, c.vida, c.rango, c.tiempo_siguiente,
            [[e.tiempo_siguiente, e.tipo] for e in sim.agenda.eventos_validos()]]


def _jugar(app):
    """Varias idas y vueltas por la conexión costosa con el cazador persiguiendo."""
    for direccion in ["E", "O", "E", "O"]:
        assert app.mover(direccion).ok
    assert app.esperar().ok


class CazadorGuardadoPruebas(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="cripta-cazador-test-")
        self.addCleanup(self.temporal.cleanup)
        self.carpeta = Path(self.temporal.name)

    def test_us5_1_replay_con_cazadores(self):
        """FR-022: el replay de una partida con cazadores y costos distintos da el mismo estado."""
        app = _app(carpeta_logs=self.carpeta)
        _jugar(app)
        app.terminar()
        replay = reproducir(app._partida.registro.ruta,
                            [FuenteCazador(_esqueleto(), 1, 4, _contenidos(), _fichas())])
        self.assertEqual(_firma(replay), _firma(app))

    def test_us5_2_guardar_y_cargar_en_persecucion(self):
        """FR-023: guardar con un cazador activo y cargar conserva rango, turno y decisiones."""
        ruta = self.carpeta / "partida.cripta"
        app = _app(ruta_guardado=ruta)
        for direccion in ["E", "O"]:
            self.assertTrue(app.mover(direccion).ok)
        antes = _firma(app)
        self.assertTrue(app.guardar().ok)
        _jugar(app)
        esperado = _firma(app)
        self.assertTrue(app.cargar().ok)
        c = _cazador(app)
        self.assertEqual(c.rango, 1000)
        self.assertEqual(_firma(app), antes)
        self.assertEqual(app._simulacion.persecucion.rango_maximo, 1000)
        _jugar(app)
        self.assertEqual(_firma(app), esperado)   # misma continuación que sin guardar

    def test_us5_3_retroceso_tras_movimiento_costoso(self):
        """FR-024, FR-017: el pergamino deshace un movimiento de costo 300 y el cazador decide bien."""
        app = _app(con_pergamino=True)
        self.assertTrue(app.recoger("sala-1-objeto-0").ok)
        for direccion in ["E", "O"]:
            self.assertTrue(app.mover(direccion).ok)
        antes = _firma(app)
        self.assertTrue(app.mover("E").ok)                      # cuesta 300 y los cazadores actúan
        self.assertNotEqual(_firma(app)[0], antes[0])
        self.assertTrue(app.usar_pergamino().ok)
        despues = _firma(app)
        self.assertEqual(despues[0], antes[0])                  # reloj
        self.assertEqual(despues[2:8], antes[2:8])              # salas, vidas, rango y turno
        c = _cazador(app)
        sim = app._simulacion
        obtenida = sim.persecucion.decidir(app._jugador.sala, c.sala,
                                           app._salas.obtener(c.sala).salidas, c.rango)
        esperada = decision_desde_cero(app._salas, c.sala, app._jugador.sala, c.rango)
        self.assertEqual(None if obtenida is None else obtenida.clave,
                         None if esperada is None else esperada.clave)

    def test_guardado_sin_cazadores_no_cambia(self):
        """FR-023: un enemigo que no es cazador se escribe y se lee igual.

        La spec 004 (FR-026) sube el formato a 3 por la línea de tiempo; el cuerpo del enemigo no cambia.
        """
        from cripta.modelo.enemigos.Errante import Errante
        self.assertEqual(VERSION_CUERPO, 3)
        errante = Errante("e-1", 5, 5, 1, 0, 100, 1, None)
        errante.nombre, errante.tipo, errante.suelta = "Errante", "t", ["x"]
        errante.regeneracion_objetivo = None
        w = EscritorBinario()
        _escribir_enemigo(w, errante)
        r = LectorBinario(w.a_bytes())
        leido = _leer_enemigo(r)
        self.assertTrue(r.al_final())
        self.assertIsNone(leido.rango)
        self.assertEqual(leido.comportamiento, "errante")


if __name__ == "__main__":
    unittest.main()
