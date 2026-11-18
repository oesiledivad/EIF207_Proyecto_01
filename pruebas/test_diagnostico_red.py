"""Diagnóstico HTTP y captura completa de entrega (spec 001, FR-030 y FR-031)."""
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.adaptadores.Diagnostico_Red import configurar_registro_red, registro_red
from cripta.controlador.VerificacionControlador import VerificacionControlador
from cripta.servicio.CriptaService import CriptaService
from herramientas.descargar_paquete_offline import descargar


class TestDiagnosticoRed(unittest.TestCase):
    def test_verificar_aplica_presupuesto_publicado_antes_del_esqueleto(self):
        """FR-019: --verificar configura el límite real, sin depender de una excepción simulada."""
        red = NetworkAdapter()
        respuesta = Mock(status_code=200)
        respuesta.json.return_value = {'id': 'prueba', 'presupuesto_solicitudes': 1}
        with patch('requests.get', return_value=respuesta) as get:
            resultado = VerificacionControlador(CriptaService(red)).verificar_cripta('prueba')
        self.assertEqual(resultado.estado, 'no_verificable')
        self.assertEqual(red.requests_made, 1)
        self.assertEqual(red.solicitudes_restantes(), 0)
        get.assert_called_once()

    def test_429_200_transporte_y_presupuesto_sin_solicitudes_extra(self):
        """FR-030: cada intento real y su espera son distinguibles del rechazo sin envío."""
        red = NetworkAdapter()
        red.fijar_presupuesto(3)
        respuestas = [Mock(status_code=429, json=Mock(return_value={'reintentar_en': 2})),
                      Mock(status_code=200, json=Mock(return_value={'criptas': []})),
                      requests.Timeout('sin respuesta')]
        with patch('requests.get', side_effect=respuestas) as get, \
             patch('cripta.adaptadores.Network_Adapter.time.sleep') as dormir, \
             self.assertLogs('cripta.red', level='INFO') as logs:
            self.assertEqual(red.crypta_list(), {'criptas': []})
            with self.assertRaises(RuntimeError):
                red.crypta_list()
            with self.assertRaises(PresupuestoAgotado):
                red.crypta_list()
        self.assertEqual(get.call_count, 3)
        self.assertEqual(red.requests_made, 3)
        dormir.assert_called_once_with(2)
        texto = '\n'.join(logs.output)
        for fragmento in ['estado=429', 'estado=200', 'numero=2', 'duracion_ms=',
                          'solicitudes=3/3', 'error=Timeout', 'motivo=presupuesto', 'segundos=2']:
            self.assertIn(fragmento, texto)

    def test_rotacion_no_duplica_y_no_escribe_en_replay(self):
        """FR-030: las capturas repetidas no duplican líneas y el diagnóstico rota separado del replay."""
        anteriores = list(registro_red.handlers)
        registro_red.handlers = []
        self.addCleanup(lambda: setattr(registro_red, 'handlers', anteriores))
        with tempfile.TemporaryDirectory() as carpeta:
            try:
                ruta = configurar_registro_red(carpeta)
                configurar_registro_red(carpeta)
                self.assertEqual(len(registro_red.handlers), 1)
                manejador = registro_red.handlers[0]
                manejador.maxBytes = 90
                self.assertEqual(manejador.backupCount, 3)
                for _ in range(20):
                    registro_red.info('intento recurso=/criptas estado=200 solicitudes=1/23')
                self.assertTrue(ruta.is_file())
                self.assertTrue(Path(str(ruta)+'.1').is_file())
                self.assertLessEqual(len(list(Path(carpeta).iterdir())), 4)
                self.assertFalse(list(Path(carpeta).glob('*partida*')))
            finally:
                for manejador in registro_red.handlers:
                    manejador.close()
                registro_red.handlers = []


class FuenteCaptura:
    def __init__(self, cambia=False):
        self.requests_made = 0
        self.cambia = cambia
        self.lotes_contenido = []
        self.lotes_fichas = []

    def get_catalog_version(self): return {'version': 'cat1'}
    def crypta_list(self): return {'criptas': [{'id': 'prueba', 'salas': 12}]}
    def crypta_details(self, cid): return {'version': 'v1', 'salas_total': 12, 'presupuesto_solicitudes': 99}
    def fijar_presupuesto(self, presupuesto): pass
    def get_crypta_version(self, cid): return {'version': 'v2' if self.cambia else 'v1'}
    def list_rooms(self, cid, pagina):
        return {'pagina': pagina, 'total_paginas': 2,
                'salas': [{'id': i} for i in (range(1, 7) if pagina == 1 else range(7, 13))]}
    def key_locations(self, cid): return {'llaves': [{'id': 'llave', 'sala': 12}]}
    def room_content(self, cid, ids):
        self.lotes_contenido.append(list(ids))
        return {'contenido': [{'sala': i, 'objetos': [f'item{i}'], 'enemigos': [], 'trampas': []} for i in ids]}
    def catalog(self, ids):
        self.lotes_fichas.append(list(ids))
        return {'entidades': [{'id': i, 'suelta': ['botin'] if i == 'item1' else []} for i in ids]}


class TestCaptura(unittest.TestCase):
    def test_paginacion_lotes_botin_y_llaves_completos(self):
        """FR-031: la captura incluye todas las páginas, lotes, llaves y referencias de botín."""
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta)/'paquete'
            fuente = FuenteCaptura()
            descargar(destino, fuente)
            self.assertTrue((destino/'cripta_prueba_salas_2.json').is_file())
            self.assertTrue((destino/'cripta_prueba_llaves.json').is_file())
            self.assertEqual([len(x) for x in fuente.lotes_contenido], [10, 2])
            self.assertTrue(all(len(x) <= 10 for x in fuente.lotes_fichas))
            self.assertIn('botin', [i for lote in fuente.lotes_fichas for i in lote])
            with self.assertRaises(FileExistsError):
                descargar(destino, fuente)

    def test_version_cambiada_no_publica_captura_parcial(self):
        """FR-031: un cambio de versión descarta toda la captura y conserva el destino ausente."""
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta)/'paquete'
            with self.assertRaisesRegex(ValueError, 'versión'):
                descargar(destino, FuenteCaptura(cambia=True))
            self.assertFalse(destino.exists())
            self.assertEqual(list(Path(carpeta).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
