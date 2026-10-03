"""Controlador de inventario.

Coordina las operaciones sobre el inventario del jugador: recoger,
soltar, equipar, usar, recorrer y ordenar vistas. Registra en el
historial los cambios invertibles.
"""

from __future__ import annotations

from cripta.controlador.GestorPartida import GestorPartida
from cripta.dto.Partida_dto import ObjetoSuelo
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.estructuras.Inventario import Inventario, ItemInventario


class InventarioControlador:
    """Operaciones de inventario.

    Args:
        gestor: Gestor de la partida activa.
        bitacora: Bitácora compartida del juego.
    """

    def __init__(self, gestor: GestorPartida, bitacora: Bitacora) -> None:
        self._gestor = gestor
        self._bitacora = bitacora

    #  Acciones

    def recoger(self, instancia_id: str) -> dict:
        inv = self._gestor.inventario
        if inv is None:
            return {"ok": False, "motivo": "Inventario no inicializado."}
        if inv.esta_lleno():
            self._bitacora.append(Mensaje("sistema", "Inventario lleno."))
            return {"ok": False, "motivo": "Inventario lleno."}

        obj = self._buscar_en_suelo(instancia_id)
        if obj is None:
            return {"ok": False, "motivo": "Ese objeto no está en el suelo."}

        item = ItemInventario(
            instancia_id=obj.id,
            tipo_id=obj.id,
            nombre=obj.nombre,
            clase="desconocido",
            peso=0,
            valor=0,
        )

        posicion_suelo = self._gestor.estado.objetos_suelo.index(obj)
        self._gestor.registrar_cambio("item_suelo_quitado", (obj, posicion_suelo))
        self._gestor.registrar_cambio("inventario_agregado", item)

        inv.agregar(item)
        self._gestor.estado.objetos_suelo.remove(obj)
        self._bitacora.append(Mensaje("jugador", f"Recogiste {obj.nombre}."))
        return {"ok": True}

    def soltar(self, instancia_id: str) -> dict:
        inv = self._gestor.inventario
        if inv is None:
            return {"ok": False, "motivo": "Inventario no inicializado."}

        posicion = inv.posicion_de(instancia_id)
        if posicion is None:
            return {"ok": False, "motivo": "No tienes ese objeto."}

        item = inv.buscar_por_id(instancia_id)
        if item is None:
            return {"ok": False, "motivo": "No tienes ese objeto."}

        self._gestor.registrar_cambio("inventario_quitado", (item, posicion))
        self._gestor.registrar_cambio("item_suelo_agregado", item.instancia_id)

        inv.soltar_por_id(instancia_id)
        self._gestor.estado.objetos_suelo.append(
            ObjetoSuelo(id=item.instancia_id, nombre=item.nombre)
        )
        self._bitacora.append(Mensaje("jugador", f"Soltaste {item.nombre}."))
        return {"ok": True}

    def equipar(self, instancia_id: str) -> dict:
        inv = self._gestor.inventario
        if inv is None:
            return {"ok": False, "motivo": "Inventario no inicializado."}

        item = inv.buscar_por_id(instancia_id)
        if item is None:
            return {"ok": False, "motivo": "No tienes ese objeto."}
        if item.clase not in ("arma", "armadura"):
            return {"ok": False, "motivo": "Ese objeto no es equipable."}

        previos: list = []
        for i in inv.items():
            if i.clase == item.clase:
                previos.append((i.instancia_id, i.equipado))
        self._gestor.registrar_cambio("item_equipado", previos)

        inv.desequipar_clase(item.clase)
        inv.equipar_por_id(instancia_id)
        self._bitacora.append(Mensaje("jugador", f"Equipaste {item.nombre}."))
        return {"ok": True}

    def usar(self, instancia_id: str) -> dict:
        inv = self._gestor.inventario
        if inv is None:
            return {"ok": False, "motivo": "Inventario no inicializado."}

        item = inv.buscar_por_id(instancia_id)
        if item is None:
            return {"ok": False, "motivo": "No tienes ese objeto."}

        if item.clase == "llave":
            return {"ok": False, "motivo": "Las llaves no se consumen."}

        # El efecto concreto lo conecta P2 (poción, antídoto, antorcha).
        self._bitacora.append(Mensaje("jugador", f"Usaste {item.nombre}."))
        return {"ok": True}

    def usar_pergamino(self) -> dict:
        """Usa un pergamino de retroceso.

        No consume tiempo virtual ni se registra como acción del jugador
        (§2.11). El pergamino se descuenta fuera del alcance de la reversión.
        """
        inv = self._gestor.inventario
        if inv is None:
            return {"ok": False, "motivo": "Inventario no inicializado."}

        pergamino = self._buscar_clase(inv, "pergamino")
        if pergamino is None:
            return {"ok": False, "motivo": "No tienes pergaminos."}

        exito = self._gestor.deshacer()
        if not exito:
            return {"ok": False, "motivo": "No hay nada que deshacer."}

        # El consumo del pergamino queda fuera del alcance de la reversión.
        inv.soltar_por_id(pergamino.instancia_id)
        self._bitacora.append(
            Mensaje("efecto", "Usaste un pergamino de retroceso.")
        )
        return {"ok": True}

    #  Recorrido

    def siguiente(self) -> dict:
        if self._gestor.inventario is None:
            return {"ok": False, "motivo": "Inventario no inicializado."}
        item = self._gestor.inventario.siguiente()
        if item is None:
            return {"ok": False, "motivo": "Inventario vacío."}
        return {"ok": True, "item": item}

    def anterior(self) -> dict:
        if self._gestor.inventario is None:
            return {"ok": False, "motivo": "Inventario no inicializado."}
        item = self._gestor.inventario.anterior()
        if item is None:
            return {"ok": False, "motivo": "Inventario vacío."}
        return {"ok": True, "item": item}

    #  Vistas

    def vista_ordenada(self, criterio: str) -> list[ItemInventario]:
        inv = self._gestor.inventario
        if inv is None:
            return []
        if criterio == "peso":
            return inv.vista_por_peso()
        if criterio == "valor":
            return inv.vista_por_valor()
        if criterio == "nombre":
            return inv.vista_por_nombre()
        return inv.items()

    #  Internos

    def _buscar_en_suelo(self, instancia_id: str):
        for o in self._gestor.estado.objetos_suelo:
            if o.id == instancia_id:
                return o
        return None

    def _buscar_clase(self, inv: Inventario, clase: str) -> ItemInventario | None:
        for item in inv.items():
            if item.clase == clase:
                return item
        return None