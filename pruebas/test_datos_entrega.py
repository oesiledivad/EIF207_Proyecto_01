"""Paquete publicado y mediciones sin E/S cronometrada (001 FR-031, 003 FR-029)."""
import io
import json
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.bench_publicada import medir_referencia_publicada
from cripta.controlador.Aplicacion import Aplicacion
from cripta.controlador.VerificacionControlador import VerificacionControlador
from cripta.dto.FactoryDto_Ficha import parsear_ficha
from cripta.servicio.CriptaService import CriptaService

PAQUETE = Path(__file__).resolve().parents[1]/'datos_entrega'


class TestDatosEntrega(unittest.TestCase):
    def test_paquete_completo_fichas_y_veredictos_sin_red(self):
        """001 FR-018, FR-031: todos los contenidos y veredictos están disponibles sin caché ni red."""
        with patch('requests.get', side_effect=AssertionError('Red en datos offline')):
            fuente = AdaptadorOffline(PAQUETE)
            for resumen in fuente.crypta_list()['criptas']:
                with self.subTest(cripta=resumen['id']):
                    fuente = AdaptadorOffline(PAQUETE)
                    servicio = CriptaService(fuente)
                    resultado = VerificacionControlador(servicio).verificar_cripta(resumen['id'])
                    self.assertIn(resultado.estado, ['resoluble', 'no_resoluble'])
                    app = Aplicacion(fuente)
                    inicio = app.iniciar_partida('Prueba', '42', resumen['id'])
                    self.assertEqual(inicio.ok, resultado.estado == 'resoluble', inicio.motivo)
                    salas = servicio.cargar_esqueleto_salas(resumen['id'], 0)
                    ids = [s.id for s in salas]
                    self.assertEqual(len(ids), resumen['salas'])
                    for i in range(0, len(ids), 10):
                        lote = fuente.room_content(resumen['id'], ids[i:i+10])
                        self.assertEqual(len(lote['contenido']), len(ids[i:i+10]))
                        tipos = CriptaService._tipos_de(lote['contenido'])
                        for j in range(0, len(tipos), 10):
                            fichas = fuente.catalog(tipos[j:j+10])
                            self.assertEqual(len(fichas['entidades']), len(tipos[j:j+10]))
            for ficha in json.loads((PAQUETE/'catalogo.json').read_text(encoding='utf-8'))['entidades']:
                parsear_ficha(ficha)

    def test_bench_publicada_determinista_sin_io_en_medicion(self):
        """003 FR-029: mapa publicado real; el cronómetro no incluye disco, red ni vista."""
        real_clock = time.perf_counter
        real_open = io.open
        midiendo = False
        def reloj():
            nonlocal midiendo
            midiendo = not midiendo
            return real_clock()
        def abrir(*args, **kwargs):
            self.assertFalse(midiendo, 'Disco dentro de la medición')
            return real_open(*args, **kwargs)
        with patch('requests.get', side_effect=AssertionError('Red en bench')), \
             patch('io.open', side_effect=abrir), patch('time.perf_counter', side_effect=reloj), \
             redirect_stdout(io.StringIO()):
            a = medir_referencia_publicada(cazadores=5, ciclos=10)
            b = medir_referencia_publicada(cazadores=5, ciclos=10)
        self.assertFalse(midiendo)
        self.assertEqual(a.huella, b.huella)
        self.assertEqual(a.salas, max(c['salas'] for c in AdaptadorOffline(PAQUETE).crypta_list()['criptas']))

    def test_ids_no_consecutivos_y_paquete_ausente(self):
        """003 FR-029: los ids del mapa no se sustituyen por índices de generación sintética."""
        with tempfile.TemporaryDirectory() as carpeta:
            p = Path(carpeta)
            archivos = {
                'criptas.json': {'criptas': [{'id': 'prueba', 'salas': 2}]},
                'cripta_prueba.json': {'id': 'prueba', 'version': 'v', 'sala_inicial': 3,
                                       'sala_salida': 90, 'llave_salida': 'llave', 'salas_total': 2},
                'cripta_prueba_salas_1.json': {'total_paginas': 1, 'salas': [
                    {'id': 3, 'salidas': {'E': {'sala': 90, 'costo': 250}}},
                    {'id': 90, 'salidas': {'O': {'sala': 3, 'costo': 250}}}]},
                'cripta_prueba_llaves.json': {'llaves': [{'id': 'llave', 'sala': 3}]}}
            for nombre, datos in archivos.items():
                (p/nombre).write_text(json.dumps(datos), encoding='utf-8')
            with redirect_stdout(io.StringIO()):
                resultado = medir_referencia_publicada(carpeta=p, cazadores=3, ciclos=4)
                self.assertIsNone(medir_referencia_publicada(carpeta=p/'ausente'))
            self.assertEqual(resultado.salas, 2)
            self.assertTrue(all(i in [3, 90] for par in resultado.huella[1] for i in par))


if __name__ == '__main__':
    unittest.main()
