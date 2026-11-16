"""Niebla de guerra: memoria de puertas (US2). Cada prueba arma su esqueleto mínimo."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import armar_aplicacion, avanzar_reloj, sala
from cripta.modelo.Conocimiento import (
    ABIERTA, CERRADA, SIN_OBSERVAR, TIPO_MEMORIA_PUERTA,
)
from cripta.modelo.Puertas import abrir_salida


def _esqueleto():
    """1 (inicial): N a 2 cerrada con cierre automático, E a 3; 2: S a 1 y N a 4 cerrada; 3: O a 1."""
    return [
        sala(1, [["N", 2, {"cerrada": True, "llave": "k", "cierre_automatico": 250}], ["E", 3]]),
        sala(2, [["S", 1], ["N", 4]]),
        sala(3, [["O", 1]]),
        sala(4, [["S", 2, {"cerrada": True, "llave": "k"}]]),
    ]


class PruebasMemoriaPuertas(unittest.TestCase):
    def setUp(self):
        self.app = armar_aplicacion(_esqueleto(), sala_inicial=1, sala_salida=4)
        self.c = self.app._exploracion.conocimiento
        self.historial = self.app._gestor.historial

    def _salida(self, sala_id, direccion):
        return self.app._salas.obtener(sala_id).salidas.obtener(direccion)

    def _entradas_de(self, clave):
        return [e for e in self.c.registro if e[1] == TIPO_MEMORIA_PUERTA and e[2] == clave]

    def _puerta_mapa(self, sala_id, direccion):
        mapa = self.app.mapa_conocido()
        conocida = next(s for s in mapa.exploradas if s.id == sala_id)
        return next(s for s in conocida.salidas if s.direccion == direccion).puerta

    def test_us2_1_cierre_automatico_recordado_abierto(self):
        """FR-009: la puerta observada abierta se sigue mostrando abierta tras cerrarse sola."""
        norte = self._salida(1, "N")
        abrir_salida(norte, 0, self.app._simulacion.agenda)   # con cierre automático a t=250
        self.assertTrue(self.app.esperar().ok)                # observa la puerta abierta
        self.assertFalse(norte.cerrada)
        self.assertEqual(self.c.memoria_puerta(norte.clave), ABIERTA)
        self.assertTrue(self.app.mover("E").ok)               # se aleja a la sala 3
        avanzar_reloj(self.app, 400)                          # la puerta cierra sola
        self.assertTrue(norte.cerrada)
        self.assertEqual(self.c.memoria_puerta(norte.clave), ABIERTA)
        self.assertEqual(self._puerta_mapa(1, "N"), "abierta")

    def test_us2_2_cambio_en_la_misma_sala(self):
        """FR-008: un cambio de una puerta de la sala actual se refleja al terminar la acción."""
        norte = self._salida(1, "N")
        abrir_salida(norte, 0, self.app._simulacion.agenda)
        self.assertTrue(self.app.esperar().ok)
        self.assertEqual(self.c.memoria_puerta(norte.clave), ABIERTA)
        pasos = 0
        while not norte.cerrada:
            pasos += 1
            self.assertLess(pasos, 20)
            self.assertTrue(self.app.esperar().ok)
            self.assertEqual(self.c.memoria_puerta(norte.clave),
                             CERRADA if norte.cerrada else ABIERTA)
        self.assertEqual(self.c.memoria_puerta(norte.clave), CERRADA)

    def test_us2_3_observa_desde_ambas_salas(self):
        """FR-007: la puerta entre A y B se observa desde A y desde B, ida y entrante."""
        ida, vuelta = self._salida(1, "N"), self._salida(2, "S")
        ida.cerrada = False       # real: abierta; la entrante real: cerrada
        vuelta.cerrada = True
        self.assertTrue(self.app.esperar().ok)                # observa desde la sala 1
        self.assertEqual(self.c.memoria_puerta(ida.clave), ABIERTA)
        self.assertEqual(self.c.memoria_puerta(vuelta.clave), CERRADA)   # la entrante
        self.assertTrue(self.app.mover("N").ok)
        ida.cerrada = True        # ahora al revés
        vuelta.cerrada = False
        self.assertTrue(self.app.esperar().ok)                # observa desde la sala 2
        self.assertEqual(self.c.memoria_puerta(vuelta.clave), ABIERTA)   # su propia salida
        self.assertEqual(self.c.memoria_puerta(ida.clave), CERRADA)      # la entrante

    def test_us2_4_volver_actualiza(self):
        """FR-009: al volver a una de sus dos salas la memoria pasa al estado real."""
        norte = self._salida(1, "N")
        self.assertEqual(self.c.memoria_puerta(norte.clave), CERRADA)
        self.assertTrue(self.app.mover("E").ok)
        norte.cerrada = False     # cambia sin que el jugador lo vea
        self.assertEqual(self.c.memoria_puerta(norte.clave), CERRADA)
        self.assertEqual(self._puerta_mapa(1, "N"), "cerrada")
        self.assertTrue(self.app.mover("O").ok)
        self.assertEqual(self.c.memoria_puerta(norte.clave), ABIERTA)
        self.assertEqual(self._puerta_mapa(1, "N"), "abierta")

    def test_us2_5_sin_observar_pasa_a_real(self):
        """FR-009a: una puerta sin observar pasa a recordar su estado real al entrar a una de sus salas."""
        self._salida(1, "N").cerrada = False
        self.c.explorar(4, self.historial, 0)                 # explorada sin entrar a ella
        sur_de_cuatro = self._salida(4, "S")
        self.assertEqual(self.c.memoria_puerta(sur_de_cuatro.clave), SIN_OBSERVAR)
        self.assertTrue(self.app.mover("N").ok)               # entra a la sala 2
        self.assertTrue(sur_de_cuatro.cerrada)
        self.assertEqual(self.c.memoria_puerta(sur_de_cuatro.clave), CERRADA)

    def test_doble_cambio_conserva_el_ultimo(self):
        """FR-008: una puerta que cambia dos veces en la sala deja el último estado."""
        norte = self._salida(1, "N")
        norte.cerrada = False
        self.assertTrue(self.app.esperar().ok)
        norte.cerrada = True
        self.assertTrue(self.app.esperar().ok)
        self.assertEqual(self.c.memoria_puerta(norte.clave), CERRADA)
        self.assertEqual([e[3] for e in self._entradas_de(norte.clave)], [ABIERTA, CERRADA])
        # dos cambios entre observaciones: queda el último, y si coincide con lo recordado no hay entrada
        norte.cerrada = False
        norte.cerrada = True
        antes = len(self._entradas_de(norte.clave))
        self.assertTrue(self.app.esperar().ok)
        self.assertEqual(len(self._entradas_de(norte.clave)), antes)

    def test_observar_sin_cambio_no_registra(self):
        """FR-037: observar sin cambios no agrega entradas al registro."""
        self.assertTrue(self.app.esperar().ok)
        antes = len(self.c.registro)
        self.assertTrue(self.app.esperar().ok)
        self.assertTrue(self.app.esperar().ok)
        self.assertEqual(len(self.c.registro), antes)


if __name__ == "__main__":
    unittest.main()
