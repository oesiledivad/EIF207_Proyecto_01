"""Niebla de guerra: explorar las vecinas con la antorcha encendida (US5)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import armar_aplicacion, contenido, sala, tiempo
from cripta.modelo.Conocimiento import (
    AVISTADA, EXPLORADA, TIPO_ESTADO_SALA,
)
from cripta.modelo.Efectos import encender_antorcha


def _esqueleto():
    """1 (inicial) con N a 2. La sala 2 tiene tres vecinas más: 3 (abierta), 4 (cerrada) y 5.

    La sala 3 sigue hacia 6, que queda fuera del alcance de la antorcha desde 2.
    """
    return [
        sala(1, [["N", 2]]),
        sala(2, [["S", 1], ["N", 3], ["E", 4, {"cerrada": True, "llave": "k"}], ["O", 5]]),
        sala(3, [["S", 2], ["N", 6]]),
        sala(4, [["O", 2]]),
        sala(5, [["E", 2]]),
        sala(6, [["S", 3]]),
    ]


def _encender(app):
    encender_antorcha(app._jugador, 800, tiempo(app), app._simulacion.agenda)
    assert app._jugador.antorcha_encendida


def _por_id(mapa, id_):
    return next(s for s in mapa.exploradas if s.id == id_)


class PruebasAntorcha(unittest.TestCase):
    def _armar(self, contenidos=None):
        app = armar_aplicacion(_esqueleto(), sala_inicial=1, sala_salida=6, contenidos=contenidos)
        return app, app._exploracion.conocimiento

    def test_us5_1_vecinas_exploradas_abiertas_y_cerradas(self):
        """FR-010: con la antorcha encendida, entrar a una sala explora todas sus vecinas,
        por salidas abiertas o cerradas."""
        app, conocimiento = self._armar()
        _encender(app)
        self.assertTrue(app.mover("N").ok)
        self.assertEqual(app._jugador.sala, 2)
        for vecina in [1, 2, 3, 4, 5]:
            self.assertEqual(conocimiento.estado(vecina), EXPLORADA, vecina)
        self.assertEqual(conocimiento.estado(6), AVISTADA)   # vecina de una vecina: solo avistada

    def test_us5_2_apendice_b_antorcha_no_activa_nada(self):
        """FR-011 (Apéndice B, caso 4): una vecina con enemigos y trampas queda explorada sin
        activar sus enemigos ni sus trampas."""
        app, conocimiento = self._armar([contenido(3, enemigos=2, trampas=1)])
        _encender(app)
        vecina = app._salas.obtener(3)
        propios = list(vecina.enemigos) + list(vecina.trampas)
        self.assertEqual(len(propios), 3)
        vida = app._jugador.vida
        self.assertTrue(app.mover("N").ok)
        self.assertEqual(conocimiento.estado(3), EXPLORADA)
        for enemigo in vecina.enemigos:
            self.assertIsNone(enemigo._proximo_evento)   # siguen dormidos
        for trampa in vecina.trampas:
            self.assertTrue(trampa.armada)
        eventos = [e for e in app._simulacion.agenda.eventos_validos() if any(e.actor is p for p in propios)]
        self.assertEqual(eventos, [])   # la agenda no ganó eventos de la vecina
        self.assertEqual(app._jugador.vida, vida)
        self.assertEqual(app._jugador.sala, 2)

    def test_us5_3_nombre_y_salidas_sin_contenido(self):
        """FR-011 y FR-009a: de la vecina explorada por antorcha el mapa conoce nombre y salidas,
        no su contenido, y sus puertas quedan sin observar."""
        app, _ = self._armar([contenido(3, enemigos=1, trampas=1)])
        _encender(app)
        self.assertTrue(app.mover("N").ok)
        conocida = _por_id(app.mapa_conocido(), 3)
        self.assertEqual(conocida.nombre, "sala 3")
        self.assertEqual({s.direccion for s in conocida.salidas}, {"S", "N"})
        self.assertFalse(hasattr(conocida, "enemigos"))
        self.assertFalse(hasattr(conocida, "trampas"))
        hacia_6 = next(s for s in conocida.salidas if s.direccion == "N")
        self.assertEqual(hacia_6.destino, 6)
        self.assertEqual(hacia_6.puerta, "sin_observar")   # no se observa desde la sala 2
        hacia_2 = next(s for s in conocida.salidas if s.direccion == "S")
        self.assertEqual(hacia_2.puerta, "abierta")   # esa sí: es una entrante de la sala actual

    def test_us5_4_antorcha_apagada_solo_avista(self):
        """FR-012: con la antorcha apagada las vecinas solo quedan avistadas."""
        app, conocimiento = self._armar()
        self.assertFalse(app._jugador.antorcha_encendida)
        self.assertTrue(app.mover("N").ok)
        self.assertEqual(conocimiento.estado(2), EXPLORADA)
        for vecina in [3, 4, 5]:
            self.assertEqual(conocimiento.estado(vecina), AVISTADA, vecina)

    def test_us5_5_encender_dentro_no_explora(self):
        """FR-010: encender la antorcha dentro de una sala no explora sus vecinas; sí las de la
        siguiente sala a la que se entra."""
        app, conocimiento = self._armar()
        self.assertTrue(app.mover("N").ok)
        _encender(app)
        for vecina in [3, 4, 5]:
            self.assertEqual(conocimiento.estado(vecina), AVISTADA, vecina)
        self.assertEqual(conocimiento.estado(6), 0)
        self.assertTrue(app.mover("N").ok)   # a la sala 3, ya con la antorcha encendida
        self.assertEqual(conocimiento.estado(6), EXPLORADA)
        self.assertEqual(conocimiento.estado(4), AVISTADA)   # no es vecina de la sala 3

    def test_antorcha_con_vecinas_ya_exploradas(self):
        """FR-010: con las vecinas ya exploradas la antorcha no altera lo conocido."""
        app, conocimiento = self._armar()
        for vecina in [3, 4, 5]:
            conocimiento.explorar(vecina, app._gestor.historial, 0)
        antes = list(conocimiento.estado_sala)
        entradas = len(conocimiento.registro)
        _encender(app)
        self.assertTrue(app.mover("N").ok)
        despues = list(conocimiento.estado_sala)
        cambios = [i for i in range(len(antes)) if antes[i] != despues[i]]
        self.assertEqual(cambios, [2])   # solo la sala a la que se entró
        nuevos = conocimiento.registro[entradas:]
        estados = [e for e in nuevos if e[1] == TIPO_ESTADO_SALA]
        self.assertEqual([e[2] for e in estados], [2])
        for vecina in [3, 4, 5]:
            self.assertEqual(conocimiento.estado(vecina), EXPLORADA)


if __name__ == "__main__":
    unittest.main()
