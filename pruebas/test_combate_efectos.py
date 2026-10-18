"""Pruebas de P2: combate, efectos, precarga y fichas en uso.

Incluye los casos del Apéndice B de P2 y la interacción de la IA y los
efectos con puertas y retroceso. Sin red, sin archivos generados y sin TUI.

    uv run python -m unittest pruebas/test_combate_efectos.py
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.test_inventario import FuentePrueba
from pruebas.test_retroceso import FuenteRetroceso, estado
from cripta.controlador.Aplicacion import Aplicacion
from cripta.controlador.CombateControlador import CombateControlador
from cripta.dto.Partida_dto import EnemigoPartida
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Salidas import Salidas
from cripta.modelo.Combate import esta_vivo
from cripta.modelo.Efectos import aplicar_veneno, cancelar_veneno, curar
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Puertas import abrir_salida
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.Simulacion import Simulacion
from cripta.modelo.enemigos.Errante import Errante
from cripta.modelo.enemigos.Rastreador import Rastreador
from cripta.servicio.CriptaService import CriptaService


def _sala(id_, salidas):
    s = Salidas()
    for direccion, destino, cerrada in salidas:
        s.agregar(direccion, destino, cerrada, "llave" if cerrada else None, 150 if cerrada else None)
    return SalaJuego(id=id_, nombre=f"Sala {id_}", salidas=s, enemigos=[], objetos=[], trampas=[])


def _jugador(vida=30, sala=99):
    return Jugador("jugador", vida, 30, 6, 2, 100, sala, 0, 10)


class FuenteDosRatas(FuenteRetroceso):
    """Sala 2 con dos ratas del mismo tipo: la ficha debe tener 2 referencias."""
    def room_content(self, cid, ids):
        respuesta = super().room_content(cid, ids)
        for sala in respuesta["contenido"]:
            if sala["sala"] == 2:
                sala["enemigos"] = [{"instancia": "rata-1", "tipo": "ent_rata_gigante"},
                                    {"instancia": "rata-2", "tipo": "ent_rata_gigante"}]
                sala["trampas"] = []
        return respuesta


class FuentePuerta(FuentePrueba):
    """Sala 1 --N (cerrada, llave de bronce, cierre a las 300)--> sala 2."""
    def list_rooms(self, cid, pagina):
        return {"salas": [
            {"id": 1, "nombre": "Inicio", "salidas": {"N": {
                "sala": 2, "cerrada": True, "llave": "itm_llave_bronce", "cierre_automatico": 300}}},
            {"id": 2, "nombre": "Salida", "salidas": {"S": {"sala": 1, "cerrada": False}}},
        ], "total_paginas": 1}

    def room_content(self, cid, ids):
        return {"contenido": [
            {"sala": sid, "enemigos": [],
             "objetos": ["itm_llave_bronce", "itm_pergamino_retroceso"] if sid == 1 else [],
             "trampas": []} for sid in ids]}


# ---------------------------------------------------------------------------
# Controladores aislados
# ---------------------------------------------------------------------------

class PruebasControladores(unittest.TestCase):
    def test_crear_enemigo_copia_ficha_y_es_identificable(self):
        dto = EnemigoPartida(id="e-201", nombre="Rata gigante", vida=12, ataque=5, defensa=1,
                             vida_max=12, velocidad=150, comportamiento="rastreador",
                             regeneracion=2, tipo="ent_rata_gigante", suelta=["itm_pocion_menor"])
        enemigo = CombateControlador.crear_enemigo(dto, 2)
        self.assertIsInstance(enemigo, Rastreador)
        self.assertEqual([enemigo.sala, enemigo.tipo, enemigo.suelta, enemigo.regeneracion_objetivo],
                         [2, "ent_rata_gigante", ["itm_pocion_menor"], 2])
        self.assertEqual(enemigo.etiqueta, "Rata gigante (e-201)")
        self.assertIsNone(enemigo._proximo_evento)  # dormido hasta que entre el jugador

    def test_comportamiento_desconocido_falla(self):
        dto = EnemigoPartida(id="x", nombre="X", vida=1, ataque=0, defensa=0, comportamiento="volador")
        with self.assertRaises(ValueError):
            CombateControlador.crear_enemigo(dto, 1)

    def test_planificar_precarga_bfs_y_tope_de_10(self):
        salas = IndiceSalas()
        for i in range(1, 16):  # pasillo lineal 1-2-...-15
            vecinos = ([["S", i - 1, False]] if i > 1 else []) + ([["N", i + 1, False]] if i < 15 else [])
            salas.insertar(i, _sala(i, vecinos))
        salas.obtener(2).contenido_cargado = True
        plan = CriptaService.planificar_precarga(salas, 15, 1)
        self.assertEqual(plan, [1, 3, 4, 5, 6, 7, 8, 9, 10, 11])  # cercanas primero, sin la 2
        self.assertTrue(CriptaService.necesita_precarga(salas, 1))


# ---------------------------------------------------------------------------
# Apéndice B (casos de P2)
# ---------------------------------------------------------------------------

class PruebasApendiceB(unittest.TestCase):
    def test_errante_sin_salidas_abiertas_espera(self):
        salas = IndiceSalas()
        salas.insertar(1, _sala(1, [["N", 2, True]]))
        errante = Errante("e", 10, 10, 1, 0, 100, 1, None)
        self.assertEqual(errante.decidir_accion(99, salas, 0, random.Random(1)), ["esperar", None])

    def test_rastreador_empate_elige_menor_id_y_rastro_caduca(self):
        salas = IndiceSalas()
        salas.insertar(5, _sala(5, [["N", 9, False], ["S", 7, False]]))
        for id_ in [7, 9]:
            vecina = _sala(id_, [])
            vecina.ultimo_tiempo_visita = 100
            salas.insertar(id_, vecina)
        rastreador = Rastreador("r", 10, 10, 1, 0, 100, 5, None)
        self.assertEqual(rastreador.decidir_accion(99, salas, 499, random.Random(1)), ["mover", 7])
        self.assertEqual(rastreador.decidir_accion(99, salas, 500, random.Random(1)), ["esperar", None])

    def test_antidoto_cancela_pulsos_y_veneno_hace_5(self):
        for cancelar, vida_esperada in [[True, 30], [False, 20]]:
            sim, jugador, salas = Simulacion(1), _jugador(sala=1), IndiceSalas()
            salas.insertar(1, _sala(1, []))
            sim.agenda.reprogramar(jugador, 1000, "accion_actor")
            aplicar_veneno(jugador, 2, 0, sim.agenda)
            if cancelar:
                cancelar_veneno(jugador, sim.agenda)
            sim.avanzar_hasta_turno_jugador(jugador, salas)
            self.assertEqual(jugador.vida, vida_esperada)

    def test_curacion_y_regeneracion_no_superan_vida_max(self):
        jugador = _jugador(vida=25)
        self.assertEqual(curar(jugador, 8), 5)
        self.assertEqual(jugador.vida, 30)
        app = Aplicacion(FuenteRetroceso())
        self.assertTrue(app.iniciar_partida("J", "42", "cripta-01").ok)
        enemigo = app._salas.obtener(2).enemigos[0]
        enemigo.regeneracion_objetivo = 50
        enemigo.vida = enemigo.vida_max - 1
        app._combate.activar_sala(app._salas.obtener(2), app._simulacion)
        for _ in range(4):
            app.esperar()
        self.assertEqual(enemigo.vida, enemigo.vida_max)

    def test_enemigo_muerto_no_actua_suelta_botin_y_libera_ficha(self):
        app = Aplicacion(FuenteDosRatas())
        self.assertTrue(app.iniciar_partida("J", "42", "cripta-01").ok)
        self.assertTrue(app.mover("N").ok)
        cache = app._cripta_service._cache_fichas
        self.assertEqual(cache._buscar("ent_rata_gigante").referencias, 2)  # dos ratas activas
        rata = app._salas.obtener(2).enemigos[0]
        rata.vida = 1
        self.assertTrue(app.atacar(rata.identificador).ok)
        self.assertFalse(esta_vivo(rata))
        self.assertNotIn(rata, app._salas.obtener(2).enemigos)
        self.assertEqual(cache._buscar("ent_rata_gigante").referencias, 1)  # la otra sigue viva
        self.assertTrue(any(o.tipo_id == "itm_pocion_menor" for o in app.estado_partida().objetos_suelo))
        self.assertTrue(any("Rata gigante (" in m.texto for m in app.bitacora().ultimos() if m))
        for evento in app._simulacion.agenda._heap:
            self.assertFalse(evento.valido and evento.actor is rata)

    def test_usar_consume_50_y_rechazo_no_gasta_tiempo(self):
        app = Aplicacion(FuenteRetroceso())
        self.assertTrue(app.iniciar_partida("J", "42", "cripta-01").ok)
        pocion = next(o for o in app.estado_partida().objetos_suelo if o.tipo_id == "itm_pocion_menor")
        self.assertTrue(app.recoger(pocion.id).ok)
        tiempo = app._simulacion.reloj.tiempo_actual
        resultado = app.usar(pocion.id)       # vida llena: cura 0 pero la poción sí tiene efecto
        self.assertTrue(resultado.ok)
        self.assertIsNone(app.inventario().buscar_por_id(pocion.id))
        self.assertEqual(app._simulacion.reloj.tiempo_actual, tiempo + 50)
        self.assertFalse(app.usar("no-existe").ok)
        self.assertEqual(app._simulacion.reloj.tiempo_actual, tiempo + 50)


# ---------------------------------------------------------------------------
# IA y efectos con puertas y retroceso
# ---------------------------------------------------------------------------

class PruebasPuertasYRetroceso(unittest.TestCase):
    def test_errante_respeta_puerta_y_queda_del_otro_lado_al_cerrarse(self):
        """Apéndice B: la puerta se cierra con el actor al otro lado; él permanece allí."""
        sim, jugador, salas = Simulacion(3), _jugador(sala=99), IndiceSalas()
        salas.insertar(1, _sala(1, [["E", 2, True]]))
        salas.insertar(2, _sala(2, [["O", 1, True]]))
        errante = Errante("e", 10, 10, 1, 0, 100, 1, None)
        salas.obtener(1).agregar_enemigo(errante)
        self.assertEqual(errante.decidir_accion(99, salas, 0, sim.azar), ["esperar", None])

        abrir_salida(salas.obtener(1).salidas.obtener("E"), 0, sim.agenda)  # se cierra en t=150
        sim.agenda.reprogramar(errante, 100, "accion_actor")
        sim.agenda.reprogramar(jugador, 400, "accion_actor")
        sim.avanzar_hasta_turno_jugador(jugador, salas)

        self.assertTrue(salas.obtener(1).salidas.obtener("E").cerrada)  # cerró en t=150
        self.assertEqual(errante.sala, 2)                                # cruzó en t=100
        self.assertIn(errante, salas.obtener(2).enemigos)
        self.assertNotIn(errante, salas.obtener(1).enemigos)

    def test_retroceso_de_abrir_puerta_cancela_su_cierre(self):
        app = Aplicacion(FuentePuerta())
        self.assertTrue(app.iniciar_partida("J", "42", "cripta-01").ok)
        for objeto in list(app.estado_partida().objetos_suelo):
            self.assertTrue(app.recoger(objeto.id).ok)
        app._gestor.historial.limpiar()
        puerta = app._salas.obtener(1).salidas.obtener("N")
        antes = estado(app)

        self.assertTrue(app.abrir("N").ok)
        self.assertFalse(puerta.cerrada)
        cierre = puerta.evento_cierre
        self.assertTrue(cierre.valido)

        self.assertTrue(app.usar_pergamino().ok)
        self.assertTrue(puerta.cerrada)
        self.assertIsNone(puerta.evento_cierre)
        self.assertNotIn(cierre, app._simulacion.agenda._heap)
        self.assertEqual(estado(app), antes)

    def test_retroceso_de_pocion_de_velocidad_restaura_tiempos(self):
        app = Aplicacion(FuenteRetroceso())
        self.assertTrue(app.iniciar_partida("J", "42", "cripta-01").ok)
        for objeto in list(app.estado_partida().objetos_suelo)[:3]:
            self.assertTrue(app.recoger(objeto.id).ok)
        app._gestor.historial.limpiar()
        from cripta.modelo.Efectos import aplicar_modificador_velocidad
        sim, jugador = app._simulacion, app._jugador
        antes = estado(app)
        self.assertTrue(app.esperar().ok)
        app._gestor.historial.abrir_intervalo()
        aplicar_modificador_velocidad(jugador, 50, 200, sim.reloj.tiempo_actual, sim.agenda)
        app._gestor.historial.cerrar_intervalo()
        self.assertEqual(jugador.velocidad, 150)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(jugador.velocidad, 100)
        self.assertIsNone(jugador.evento_fin_velocidad)
        self.assertEqual(estado(app), antes)

    def test_retroceso_de_muerte_revive_y_reprotege_fichas(self):
        app = Aplicacion(FuenteDosRatas())
        self.assertTrue(app.iniciar_partida("J", "42", "cripta-01").ok)
        for objeto in list(app.estado_partida().objetos_suelo)[:4]:
            self.assertTrue(app.recoger(objeto.id).ok)
        self.assertTrue(app.mover("N").ok)
        rata = app._salas.obtener(2).enemigos[0]
        rata.vida = 1
        antes = estado(app)
        self.assertTrue(app.atacar(rata.identificador).ok)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(estado(app), antes)
        self.assertTrue(esta_vivo(rata))
        self.assertIn(rata, app._salas.obtener(2).enemigos)
        cache = app._cripta_service._cache_fichas
        self.assertEqual(cache._buscar("ent_rata_gigante").referencias, 2)
        self.assertEqual(app.estado_partida().enemigos_derrotados, 0)


if __name__ == "__main__":
    unittest.main()
