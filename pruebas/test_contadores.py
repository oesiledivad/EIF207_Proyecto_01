"""Contadores monótonos de la spec 003: cambios de puertas y reversiones del historial.

    uv run python -m unittest pruebas.test_contadores
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.estructuras.Historial_Retroceso import Historial_Retroceso
from cripta.estructuras.Salidas import SalidaSimple
from cripta.modelo.Puertas import abrir_salida, procesar_cierre_puerta


def _salida(cerrada=True):
    return SalidaSimple("N", 2, cerrada)


def _nada(etiqueta, datos):
    return None


class ContadoresPruebas(unittest.TestCase):
    def test_cambios_puertas_sube_al_abrir_y_al_cerrar(self):
        """FR-017: abrir_salida y procesar_cierre_puerta suben `cambios_puertas` en 1."""
        agenda = HeapAgendaEventos()
        salida = _salida()
        self.assertEqual(agenda.cambios_puertas, 0)
        abrir_salida(salida, 0, agenda)
        self.assertEqual(agenda.cambios_puertas, 1)
        procesar_cierre_puerta(salida, agenda)
        self.assertEqual(agenda.cambios_puertas, 2)
        self.assertTrue(salida.cerrada)

    def test_cambios_puertas_no_baja_al_revertir(self):
        """FR-017: revertir el intervalo deshace la puerta pero el contador no baja."""
        historial = Historial_Retroceso()
        agenda = HeapAgendaEventos(historial)
        salida = _salida()
        historial.abrir_intervalo()
        abrir_salida(salida, 0, agenda)
        self.assertEqual(agenda.cambios_puertas, 1)
        historial.revertir_abierto(_nada)
        self.assertEqual(agenda.cambios_puertas, 1)

    def test_reversiones_cuenta_revertir_abierto_y_deshacer(self):
        """FR-017, FR-024: `reversiones` empieza en 0 y sube con cada reversión; limpiar no la reinicia."""
        historial = Historial_Retroceso()
        self.assertEqual(historial.reversiones, 0)
        historial.abrir_intervalo()
        historial.revertir_abierto(_nada)
        self.assertEqual(historial.reversiones, 1)
        historial.abrir_intervalo()
        historial.cerrar_intervalo()
        self.assertTrue(historial.deshacer(_nada))
        self.assertEqual(historial.reversiones, 2)
        self.assertFalse(historial.deshacer(_nada))   # sin intervalos no hay reversión
        self.assertEqual(historial.reversiones, 2)
        historial.limpiar()
        self.assertEqual(historial.reversiones, 2)

    def test_agenda_sin_historial_cambia_atributos(self):
        """FR-017: una agenda sin historial sigue cambiando los atributos de la salida."""
        agenda = HeapAgendaEventos()
        salida = _salida()
        abrir_salida(salida, 0, agenda)
        self.assertFalse(salida.cerrada)


if __name__ == "__main__":
    unittest.main()
