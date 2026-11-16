"""Clave de salida y lista de entrantes al ensamblar las salas."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.controlador.ExploracionControlador import ExploracionControlador
from cripta.dto.Partida_dto import SalaModelo, SalidaVecina


def _vecina(direccion, destino):
    return SalidaVecina(direccion=direccion, sala_id=destino, nombre="", cerrada=False, llave="",
                        transitable=True, es_salida_final=False, tiene_enemigos=False,
                        tiene_objetos=False)


def _esqueleto():
    return [
        SalaModelo(0, "a", "", [_vecina("N", 1), _vecina("E", 2)]),
        SalaModelo(1, "b", "", [_vecina("S", 0), _vecina("O", 2), _vecina("E", 99)]),
        SalaModelo(2, "c", "", [_vecina("O", 0), _vecina("S", 1)]),
    ]


class PruebasEntrantes(unittest.TestCase):
    def setUp(self):
        self.ctl = ExploracionControlador(None)
        self.ctl.ensamblar_salas(_esqueleto())

    def _salidas(self):
        for sala in self.ctl.salas._datos:
            if sala is not None:
                for salida in sala.salidas:
                    yield sala.id, salida

    def test_clave_por_origen_y_direccion(self):
        """FR-007: clave = origen * 4 + índice de dirección (N 0, S 1, E 2, O 3)."""
        indice = [["N", 0], ["S", 1], ["E", 2], ["O", 3]]
        for origen, salida in self._salidas():
            numero = next(i for d, i in indice if d == salida.direccion)
            self.assertEqual(salida.clave, origen * 4 + numero)
            self.assertEqual(salida.clave // 4, origen)

    def test_claves_unicas(self):
        """FR-007: las claves no se repiten."""
        claves = [s.clave for _, s in self._salidas()]
        for i in range(len(claves)):
            for j in range(i + 1, len(claves)):
                self.assertNotEqual(claves[i], claves[j])

    def test_entrantes_exactos(self):
        """FR-022: entrantes[v] tiene exactamente las salidas con destino v."""
        for v in range(3):
            esperadas = [s.clave for _, s in self._salidas() if s.sala_destino == v]
            self.assertEqual([s.clave for s in self.ctl.entrantes[v]], esperadas)

    def test_destino_inexistente_no_rompe(self):
        """FR-022: una salida hacia una sala inexistente no rompe el ensamblado."""
        self.assertTrue(any(s.sala_destino == 99 for _, s in self._salidas()))
        for v in range(3):
            for s in self.ctl.entrantes[v]:
                self.assertEqual(s.sala_destino, v)


if __name__ == "__main__":
    unittest.main()
