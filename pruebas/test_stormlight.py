"""Integracion del escenario offline Stormlight y referencias de sus datos."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.controlador.Aplicacion import Aplicacion
from cripta.dto.FactoryDto_Ficha import parsear_ficha
from cripta.replay.reproductor import reproducir
from pruebas.test_replay import firma

DATOS = Path(__file__).resolve().parents[1] / "datos_prueba"
CRIPTA = "cripta-stormlight"


class FuenteMedida(AdaptadorOffline):
    def __init__(self):
        super().__init__(DATOS)
        self.lotes_salas = []
        self.lotes_fichas = []

    def room_content(self, cid, ids):
        self.lotes_salas.append(list(ids))
        return super().room_content(cid, ids)

    def catalog(self, ids):
        self.lotes_fichas.append(list(ids))
        return super().catalog(ids)


class PruebasStormlight(unittest.TestCase):
    def test_referencias_paginas_llaves_y_catalogo_completos(self):
        fuente = AdaptadorOffline(DATOS)
        detalles = fuente.crypta_details(CRIPTA)
        salas = []
        for pagina in range(1, detalles["paginas"] + 1):
            pagina_datos = fuente.list_rooms(CRIPTA, pagina)
            self.assertEqual(pagina_datos["total_paginas"], detalles["paginas"])
            salas.extend(pagina_datos["salas"])
        self.assertEqual([s["id"] for s in salas], list(range(1, 21)))
        catalogo = fuente._leer("catalogo.json")["entidades"]
        nuevas = [f for f in catalogo if f["id"].startswith("sl_")]
        self.assertEqual(len(nuevas), 28)
        for ficha in nuevas:
            parsear_ficha(ficha)
        ids = [f["id"] for f in catalogo]
        for posicion, tipo in enumerate(ids):
            self.assertNotIn(tipo, ids[:posicion])
        contenido = fuente._leer(f"cripta_{CRIPTA}_contenido.json")["contenido"]
        self.assertEqual([c["sala"] for c in contenido], list(range(1, 21)))
        instancias = []
        for sala in contenido:
            referencias = sala["objetos"] + [e["tipo"] for e in sala["enemigos"] + sala["trampas"]]
            for referencia in referencias:
                self.assertIn(referencia, ids)
            for entidad in sala["enemigos"] + sala["trampas"]:
                self.assertNotIn(entidad["instancia"], instancias)
                instancias.append(entidad["instancia"])
        for ficha in nuevas:
            for botin in ficha.get("suelta", []):
                self.assertIn(botin, ids)
        visitadas, cola = [], [detalles["sala_inicial"]]
        while cola:
            sid = cola.pop(0)
            if sid in visitadas:
                continue
            visitadas.append(sid)
            for salida in salas[sid - 1]["salidas"].values():
                self.assertIn(salida["sala"], range(1, 21))
                if not salida.get("cerrada", False):
                    cola.append(salida["sala"])
                else:
                    self.assertIn(salida["llave"], ids)
        for llave in ("sl_llave_archivo", "sl_llave_radiante"):
            self.assertTrue(any(llave in sala["objetos"] and sala["sala"] in visitadas
                                for sala in contenido))
        entradas_salida = [v for s in salas for v in s["salidas"].values() if v["sala"] == 20]
        self.assertEqual(len(entradas_salida), 2)
        self.assertTrue(all(v["cerrada"] and v["llave"] == detalles["llave_salida"]
                            for v in entradas_salida))
        self.assertEqual(fuente.get_crypta_version(CRIPTA)["version"], detalles["version"])
        self.assertTrue(any(c["id"] == CRIPTA for c in fuente.crypta_list()["criptas"]))

    def test_precarga_mas_de_diez_salas_en_lotes_sin_red(self):
        fuente = FuenteMedida()
        app = Aplicacion(fuente)
        resultado = app.iniciar_partida("Radiante", "42", CRIPTA)
        self.assertTrue(resultado.ok, resultado.motivo)
        self.assertEqual(len(fuente.lotes_salas[0]), 10)
        self.assertEqual(len(app.estado_partida().salas_conocidas), 20)
        for direccion in ("S", "S", "S", "E"):
            resultado = app.mover(direccion)
            self.assertTrue(resultado.ok, resultado.motivo)
        self.assertGreater(len(fuente.lotes_salas), 1)
        self.assertTrue(all(0 < len(lote) <= 10 for lote in fuente.lotes_salas + fuente.lotes_fichas))
        self.assertEqual(app.solicitudes_usadas(), 0)
        self.assertLessEqual(app._cripta_service._cache_fichas.tamano, 25)
        self.assertTrue(app.recoger("sala-17-objeto-0").ok)
        self.assertTrue(app.mover("E").ok)
        self.assertTrue(app.mover("E").ok)
        antes = app.estado_partida().reloj_virtual
        self.assertFalse(app.mover("E").ok)  # La apertura de puertas aun esta pendiente.
        self.assertEqual(app.estado_partida().reloj_virtual, antes)

    def test_inventario_veneno_velocidad_dos_retrocesos_y_replay(self):
        with tempfile.TemporaryDirectory(prefix="cripta-stormlight-test-") as carpeta:
            app = Aplicacion(AdaptadorOffline(DATOS), carpeta_logs=carpeta)
            resultado = app.iniciar_partida("Radiante", "42", CRIPTA)
            self.assertTrue(resultado.ok, resultado.motivo)
            for objeto in list(app.estado_partida().objetos_suelo):
                self.assertTrue(app.recoger(objeto.id).ok)
            self.assertTrue(app.equipar("sala-1-objeto-0").ok)
            self.assertTrue(app.equipar("sala-1-objeto-1").ok)
            self.assertTrue(app.mover("E").ok)
            self.assertIsNotNone(app._jugador.evento_veneno)
            self.assertTrue(app.recoger("sala-2-objeto-0").ok)
            self.assertTrue(app.inventario().esta_lleno())
            antes = app.estado_partida().reloj_virtual
            self.assertFalse(app.recoger("sala-2-objeto-1").ok)
            self.assertEqual(app.estado_partida().reloj_virtual, antes)
            self.assertTrue(app.usar("sala-2-objeto-0").ok)
            self.assertIsNone(app._jugador.evento_veneno)
            self.assertTrue(app.usar("sala-1-objeto-2").ok)
            self.assertTrue(app._jugador.antorcha_encendida)
            self.assertTrue(app.mover("E").ok)
            self.assertTrue(app.recoger("sala-3-objeto-0").ok)
            self.assertTrue(app.usar("sala-3-objeto-0").ok)
            self.assertGreater(app._jugador.velocidad, 100)
            antes = app.estado_partida().reloj_virtual
            pergaminos = sum(i.clase == "pergamino_retroceso" for i in app.inventario().items())
            self.assertTrue(app.esperar().ok)
            self.assertTrue(app.esperar().ok)
            self.assertTrue(app.usar_pergamino().ok)
            self.assertTrue(app.usar_pergamino().ok)
            self.assertEqual(app.estado_partida().reloj_virtual, antes)
            self.assertEqual(sum(i.clase == "pergamino_retroceso" for i in app.inventario().items()),
                             pergaminos - 2)
            app.terminar()
            self.assertEqual(app._partida.registro.ruta.name, "cripta_stormlight_partida_00001.log")
            self.assertTrue((Path(carpeta) / "puntajes.json").exists())
            replay = reproducir(app._partida.registro.ruta, [AdaptadorOffline(DATOS)])
            self.assertEqual(firma(app), firma(replay))
