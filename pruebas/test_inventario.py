"""Pruebas sin red de inventario, equipo y deltas."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.controlador.Aplicacion import Aplicacion
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.controlador.GestorPartida import GestorPartida
from cripta.controlador.InventarioControlador import InventarioControlador
from cripta.dto.Partida_dto import ObjetoSuelo
from cripta.estructuras.Bitacora import Bitacora
from cripta.estructuras.Inventario import Inventario, ItemInventario


class FuentePrueba(AdaptadorOffline):
    """Dos salas sintéticas; el catálogo local aporta fichas reales."""
    def __init__(self):
        super().__init__(Path(__file__).resolve().parents[1] / "datos_offline")

    def crypta_details(self, cid):
        datos = super().crypta_details(cid)
        datos["salas_total"] = 2
        datos["sala_salida"] = 2
        return datos

    def list_rooms(self, cid, pagina):
        return {"salas": [
            {"id": 1, "nombre": "Inicio", "salidas": {"N": {"sala": 2, "cerrada": False}}},
            {"id": 2, "nombre": "Salida", "salidas": {"S": {"sala": 1, "cerrada": False}}},
        ], "total_paginas": 1}

    def room_content(self, cid, ids):
        objetos = ["itm_daga_oxidada", "itm_daga_oxidada",
                   "itm_coraza_cuero", "itm_pocion_menor"]
        return {"contenido": [
            {"sala": sid, "enemigos": [], "objetos": objetos if sid == 1 else [],
             "trampas": []} for sid in ids
        ]}


class InventarioPruebas(unittest.TestCase):
    def test_orden_descendente_estable_sin_mutar_inventario(self):
        from cripta.estructuras.Ordenamientos import insertion_sort, merge_sort, ordenar
        for algoritmo in [insertion_sort, merge_sort, ordenar]:
            datos = [[i % 3, i] for i in range(45)]
            esperado = [fila for clave in [2, 1, 0] for fila in datos if fila[0] == clave]
            self.assertEqual(algoritmo(datos.copy(), key=lambda fila: fila[0], reverse=True), esperado)
            self.assertEqual(algoritmo(["a", "c", "b"], reverse=True), ["c", "b", "a"])
            self.assertEqual(algoritmo([], reverse=True), [])
        self.gestor.reiniciar_inventario(10)
        inv = self.gestor.inventario
        for i, nombre in enumerate(["Beta", "Alfa", "Gamma"]):
            inv.agregar(ItemInventario(str(i), "tipo", nombre, "pocion", 1, i))
        antes = inv.items()
        seleccionado = inv.item_actual()
        self.assertEqual([i.nombre for i in inv.vista_ordenada(lambda i: i.nombre, True)],
                         ["Gamma", "Beta", "Alfa"])
        self.assertEqual(inv.items(), antes)
        self.assertIs(inv.item_actual(), seleccionado)

    def test_soltar_actual_no_busca_por_id_ni_posicion(self):
        self.gestor.reiniciar_inventario(10)
        inv = self.gestor.inventario
        for i in range(10):
            inv.agregar(ItemInventario(str(i), "tipo", "Objeto", "pocion", 1, 1))
        orden = [item.instancia_id for item in inv.items()]
        for id_ in ["0", "4", "9"]:
            inv.seleccionar(id_)
            with patch.object(inv, "posicion_de", side_effect=AssertionError("Búsqueda de posición")), \
                    patch.object(inv, "_buscar_nodo", side_effect=AssertionError("Búsqueda por id")):
                self.assertTrue(self.accion(lambda: self.control.soltar(id_, self.jugador)).ok)
            self.assertTrue(self.gestor.deshacer())
            self.assertEqual([item.instancia_id for item in inv.items()], orden)

    def test_reinsercion_omite_ancla_pergamino_consumida(self):
        inv = self.gestor.inventario
        for id_, clase in [["a", "pocion"], ["p", "pergamino_retroceso"], ["b", "pocion"]]:
            inv.agregar(ItemInventario(id_, "tipo", id_, clase, 1, 1))
        inv.seleccionar("a")
        self.assertTrue(self.accion(lambda: self.control.soltar("a", self.jugador)).ok)
        inv.soltar_por_id("p")
        self.assertTrue(self.gestor.deshacer())
        self.assertEqual([item.instancia_id for item in inv.items()], ["b", "a"])

    def setUp(self):
        self.gestor = GestorPartida()
        self.gestor.reiniciar_inventario(4)
        self.jugador = SimpleNamespace(ataque=6, defensa=2)
        ficha = SimpleNamespace(id="arma", nombre="Espada", clase="arma",
                                peso=2, valor=15, ataque_bonus=3)
        servicio = SimpleNamespace(obtener_ficha_garantizada=lambda tipo: ficha)
        self.control = InventarioControlador(self.gestor, Bitacora(), servicio)

    def accion(self, funcion):
        self.gestor.abrir_intervalo()
        resultado = funcion()
        if resultado.ok:
            self.gestor.cerrar_intervalo()
        else:
            self.gestor.descartar_intervalo()
        return resultado

    def test_recoger_equipar_soltar_y_revertir(self):
        suelo = self.gestor.estado.objetos_suelo
        suelo.extend([ObjetoSuelo("a", "Espada", "arma"),
                      ObjetoSuelo("b", "Espada", "arma")])
        for id_ in ["a", "b"]:
            self.assertTrue(self.accion(lambda: self.control.recoger(id_)).ok)
        inv = self.gestor.inventario
        self.assertEqual(inv.buscar_por_id("a").peso, 2)
        self.assertEqual([i.instancia_id for i in inv.items()], ["b", "a"])
        self.assertTrue(self.accion(lambda: self.control.equipar("a", self.jugador)).ok)
        self.assertEqual(self.jugador.ataque, 9)
        self.assertTrue(self.accion(lambda: self.control.equipar("b", self.jugador)).ok)
        self.assertEqual(self.jugador.ataque, 9)
        self.assertFalse(inv.buscar_por_id("a").equipado)
        self.assertTrue(self.accion(lambda: self.control.soltar("b", self.jugador)).ok)
        self.assertEqual(self.jugador.ataque, 6)
        self.assertEqual(suelo[0].tipo_id, "arma")
        self.assertTrue(self.gestor.deshacer())
        self.assertEqual(self.jugador.ataque, 9)
        self.assertIs(suelo, self.gestor.estado.objetos_suelo)
        self.assertEqual(suelo, [])
        self.assertTrue(self.gestor.deshacer())
        self.assertTrue(inv.buscar_por_id("a").equipado)
        self.assertEqual([i.instancia_id for i in inv.items()], ["a", "b"])

    def test_ciclo_completo_costos_instancias_cache_y_consumible(self):
        app = Aplicacion(FuentePrueba())
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
        objetos = list(app.estado_partida().objetos_suelo)
        self.assertNotEqual(objetos[0].id, objetos[1].id)
        for objeto in objetos:
            self.assertTrue(app.recoger(objeto.id).ok)
        self.assertEqual(app.estado_partida().reloj_virtual, 100)
        for objeto in objetos[:3]:
            self.assertTrue(app.equipar(objeto.id).ok)
        self.assertEqual(app.estado_partida().jugador_ataque, 9)
        self.assertEqual(app.estado_partida().jugador_defensa, 4)
        self.assertEqual(app.estado_partida().reloj_virtual, 250)
        self.assertTrue(app.mover("N").ok)
        cache = app._cripta_service._cache_fichas
        self.assertEqual(cache._buscar("itm_daga_oxidada").referencias, 2)
        self.assertTrue(app.soltar(objetos[1].id).ok)
        self.assertEqual(app.estado_partida().jugador_ataque, 6)
        self.assertEqual(app.estado_partida().objetos_suelo[0].tipo_id, "itm_daga_oxidada")
        self.assertTrue(app.recoger(objetos[1].id).ok)
        self.assertTrue(app.usar(objetos[3].id).ok)
        self.assertIsNone(app.inventario().buscar_por_id(objetos[3].id))
        self.assertEqual(cache._buscar("itm_pocion_menor").referencias, 0)
        self.assertEqual(app.estado_partida().reloj_virtual, 450)

    def test_reinsertar_final_y_vista_sin_mutar(self):
        inv = Inventario(3)
        for id_ in ["a", "b", "c"]:
            inv.agregar(ItemInventario(id_, id_, id_, "arma", 1, 1))
        item = inv.soltar_por_id("a")
        self.assertTrue(inv.reinsertar_en(item, 2))
        self.assertEqual([i.instancia_id for i in inv.items()], ["c", "b", "a"])
        self.assertEqual([i.instancia_id for i in inv.vista_por_nombre()], ["a", "b", "c"])
        self.assertEqual([i.instancia_id for i in inv.items()], ["c", "b", "a"])

    def test_inventario_lleno_rechaza_sin_historial(self):
        inv = self.gestor.inventario
        for n in range(4):
            inv.agregar(ItemInventario(str(n), "arma", "Espada", "arma", 2, 15))
        self.gestor.estado.objetos_suelo.append(ObjetoSuelo("nuevo", "Espada", "arma"))
        self.assertFalse(self.accion(lambda: self.control.recoger("nuevo")).ok)
        self.assertEqual(len(self.gestor.historial), 0)
        self.assertEqual(len(self.gestor.estado.objetos_suelo), 1)


if __name__ == "__main__":
    unittest.main()
