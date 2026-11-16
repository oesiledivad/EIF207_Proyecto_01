"""Niebla de guerra: estados de sala, mapa conocido y vista derivada del conocimiento (US1)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import armar_aplicacion, contenido, sala
from cripta.modelo.Conocimiento import (
    ABIERTA, AVISTADA, CERRADA, DESCONOCIDA, EXPLORADA, SIN_OBSERVAR,
)


def _esqueleto():
    """1 (inicial) con N a 2 y E a 3; 2 con N a 4; 4 con S a 2; 5 desconectada."""
    return [
        sala(1, [["N", 2, {"costo": 30}], ["E", 3, {"cerrada": True, "llave": "k"}]]),
        sala(2, [["S", 1], ["N", 4, {"costo": 7}]]),
        sala(3, [["O", 1]]),
        sala(4, [["S", 2]]),
        sala(5, [["S", 4]]),
    ]


def _por_id(mapa, id_):
    return next(s for s in mapa.exploradas if s.id == id_)


def _salida(sala_conocida, direccion):
    return next(s for s in sala_conocida.salidas if s.direccion == direccion)


class PruebasConocimiento(unittest.TestCase):
    def setUp(self):
        self.app = armar_aplicacion(_esqueleto(), sala_inicial=1, sala_salida=4)
        self.conocimiento = self.app._exploracion.conocimiento

    def test_us1_1_instante_cero(self):
        """FR-002, FR-003 y FR-018: al inicio solo la sala inicial está explorada."""
        mapa = self.app.mapa_conocido()
        self.assertEqual([s.id for s in mapa.exploradas], [1])
        self.assertEqual(mapa.avistadas, [2, 3])
        inicial = _por_id(mapa, 1)
        self.assertEqual([[s.direccion, s.destino, s.destino_estado] for s in inicial.salidas],
                         [["N", 2, "avistada"], ["E", 3, "avistada"]])
        self.assertEqual(self.conocimiento.estado(4), DESCONOCIDA)
        self.assertEqual(self.conocimiento.estado(5), DESCONOCIDA)

    def test_us1_2_entrar_a_avistada(self):
        """FR-002 y FR-003: entrar a una avistada la explora y avista sus destinos."""
        self.assertEqual(self.conocimiento.estado(2), AVISTADA)
        self.assertEqual(self.conocimiento.estado(4), DESCONOCIDA)
        self.assertTrue(self.app.mover("N").ok)
        self.assertEqual(self.conocimiento.estado(2), EXPLORADA)
        self.assertEqual(self.conocimiento.estado(4), AVISTADA)
        self.assertEqual(self.conocimiento.estado(1), EXPLORADA)
        self.assertEqual(self.conocimiento.estado(5), DESCONOCIDA)

    def test_us1_3_nunca_desconocidas(self):
        """FR-004, FR-006 y SC-002: el mapa no incluye salas desconocidas."""
        for direccion in ["N", "N", "S", "S"]:
            self.assertTrue(self.app.mover(direccion).ok)
            mapa = self.app.mapa_conocido()
            visibles = [s.id for s in mapa.exploradas] + list(mapa.avistadas)
            for id_ in visibles:
                self.assertNotEqual(self.conocimiento.estado(id_), DESCONOCIDA)
            for id_ in mapa.avistadas:
                self.assertIsInstance(id_, int)  # de una avistada solo se expone el id
            self.assertNotIn(5, visibles)
        self.assertEqual(self.conocimiento.estado(999), DESCONOCIDA)
        self.assertEqual(self.conocimiento.estado(-3), DESCONOCIDA)

    def test_us1_4_costo_y_puerta_recordada(self):
        """FR-005 y FR-023: cada salida indica costo y puerta recordada; sin costo vale 100."""
        inicial = _por_id(self.app.mapa_conocido(), 1)
        norte, este = _salida(inicial, "N"), _salida(inicial, "E")
        self.assertEqual([norte.costo, norte.puerta], [30, "abierta"])
        self.assertEqual([este.costo, este.puerta], [100, "cerrada"])
        sala_dos = self.app._salas.obtener(2)
        self.assertEqual(self.conocimiento.memoria_puerta(sala_dos.salidas.obtener("S").clave),
                         ABIERTA)  # entrante a la sala inicial, observada desde ella
        self.assertEqual(self.conocimiento.memoria_puerta(
            self.app._salas.obtener(1).salidas.obtener("E").clave), CERRADA)

    def test_us1_5_puertas_sin_observar(self):
        """FR-005 y FR-009a: explorar sin entrar deja las puertas sin observar."""
        self.conocimiento.explorar(4, self.app._gestor.historial, 0)
        mapa = self.app.mapa_conocido()
        cuatro = _por_id(mapa, 4)
        self.assertEqual([s.puerta for s in cuatro.salidas], ["sin_observar"])
        self.assertEqual(self.conocimiento.memoria_puerta(
            self.app._salas.obtener(4).salidas.obtener("S").clave), SIN_OBSERVAR)

    def test_vecindad_no_revela_contenido(self):
        """FR-011 y FR-014: la vecindad no copia enemigos ni objetos de las vecinas."""
        contenidos = [contenido(2, enemigos=2), contenido(3, enemigos=1)]
        app = armar_aplicacion(_esqueleto(), sala_inicial=1, sala_salida=3, contenidos=contenidos)
        for vecina in app.estado_partida().vecindad:
            self.assertFalse(vecina.tiene_enemigos)
            self.assertFalse(vecina.tiene_objetos)
            self.assertFalse(vecina.es_salida_final)  # la vecina 3 solo está avistada
            self.assertEqual(vecina.estado_vecina, "avistada")
        self.assertFalse(app.mover("E").ok)  # puerta cerrada: no entra a 3
        self.assertTrue(app.mover("N").ok)
        self.assertTrue(app.mover("S").ok)

    def test_vecindad_oculta_nombre_de_avistadas(self):
        """FR-004: de una sala avistada la vecindad solo expone el id."""
        for vecina in self.app.estado_partida().vecindad:
            self.assertEqual(vecina.nombre, f"Sala {vecina.sala_id}")

    def test_vecindad_es_salida_final_solo_si_explorada(self):
        """FR-011 y C7: `es_salida_final` aparece solo para vecinas exploradas."""
        self.assertTrue(self.app.mover("N").ok)
        en_dos = self.app.estado_partida().vecindad
        self.assertFalse(next(v for v in en_dos if v.sala_id == 4).es_salida_final)
        self.assertTrue(self.app.mover("N").ok)   # explora la sala 4 (la salida)
        self.assertTrue(self.app.mover("S").ok)   # vuelve a la sala 2
        en_dos = self.app.estado_partida().vecindad
        cuatro = next(v for v in en_dos if v.sala_id == 4)
        self.assertTrue(cuatro.es_salida_final)
        self.assertEqual(cuatro.estado_vecina, "explorada")
        self.assertEqual(cuatro.costo, 7)

    def test_conocimiento_no_inicializado_es_inocuo(self):
        """FR-014: una Aplicacion armada sin iniciar_partida ejecuta una accion sin error."""
        from cripta.controlador.Aplicacion import Aplicacion
        from pruebas.apoyo_niebla import FuenteNiebla
        app = Aplicacion(FuenteNiebla(_esqueleto()))
        self.assertFalse(app._exploracion.conocimiento.inicializado)
        conocimiento = app._exploracion.conocimiento
        conocimiento.explorar(1, app._gestor.historial, 0)
        conocimiento.entrar(2, False, app._gestor.historial, 0)
        self.assertEqual(conocimiento.estado(1), DESCONOCIDA)
        self.assertEqual(conocimiento.memoria_puerta(0), SIN_OBSERVAR)
        mapa = app.mapa_conocido()
        self.assertEqual([mapa.exploradas, mapa.avistadas], [[], []])


if __name__ == "__main__":
    unittest.main()
