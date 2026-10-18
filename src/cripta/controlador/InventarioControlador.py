"""Controlador de inventario.

Coordina las operaciones sobre el inventario del jugador: recoger,
soltar, equipar, usar y recorrer. Registra en el
historial los cambios invertibles.
"""

from __future__ import annotations

from cripta.replay.reproductor import ErrorRegistro
from cripta.controlador.GestorPartida import GestorPartida
from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.servicio.CriptaService import CriptaService
from cripta.dto.Partida_dto import ObjetoSuelo
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.estructuras.Inventario import ItemInventario


class InventarioControlador:
    """Operaciones de inventario.

    Args:
        gestor: Gestor de la partida activa.
        bitacora: Bitácora compartida del juego.
    """

    def __init__(self, gestor: GestorPartida, bitacora: Bitacora, servicio: CriptaService) -> None:
        self._gestor = gestor
        self._bitacora = bitacora
        self._servicio = servicio

    #  Acciones

    def recoger(self, instancia_id: str) -> ResultadoAccion:
        inv = self._gestor.inventario
        if inv is None:
            return ResultadoAccion.fallo("Inventario no inicializado.")
        if inv.esta_lleno():
            self._bitacora.append(Mensaje("sistema", "Inventario lleno."))
            return ResultadoAccion.fallo("Inventario lleno.")

        obj = self._buscar_en_suelo(instancia_id)
        if obj is None:
            return ResultadoAccion.fallo("Ese objeto no está en el suelo.")

        try:
            ficha = self._servicio.obtener_ficha_garantizada(obj.tipo_id or obj.id)
        except (PresupuestoAgotado, RuntimeError) as error:
            return ResultadoAccion.fallo(str(error))
        if ficha is None or ficha.clase in ["enemigo", "trampa"]:
            return ResultadoAccion.fallo("El objeto no tiene una ficha válida.")
        item = ItemInventario(
            instancia_id=obj.id,
            tipo_id=ficha.id,
            nombre=ficha.nombre,
            clase=ficha.clase,
            peso=ficha.peso,
            valor=ficha.valor,
            ataque_bonus=getattr(ficha, "ataque_bonus", 0),
            defensa_bonus=getattr(ficha, "defensa_bonus", 0),
        )

        posicion_suelo = self._gestor.estado.objetos_suelo.index(obj)
        if item.clase != "pergamino_retroceso":
            self._gestor.registrar_cambio("item_suelo_quitado", [self._gestor.estado.objetos_suelo, obj, posicion_suelo])
            self._gestor.registrar_cambio("inventario_agregado", item)

        inv.agregar(item)
        self._gestor.estado.objetos_suelo.remove(obj)
        self._bitacora.append(Mensaje("jugador", f"Recogiste {obj.nombre}."))
        return ResultadoAccion.exito()

    def soltar(self, instancia_id: str, jugador) -> ResultadoAccion:
        inv = self._gestor.inventario
        if inv is None:
            return ResultadoAccion.fallo("Inventario no inicializado.")

        posicion = inv.posicion_de(instancia_id)
        if posicion is None:
            return ResultadoAccion.fallo("No tienes ese objeto.")

        item = inv.buscar_por_id(instancia_id)
        if item is None:
            return ResultadoAccion.fallo("No tienes ese objeto.")

        if item.clase != "pergamino_retroceso":
            self._gestor.registrar_cambio("inventario_quitado", [item, posicion])
            self._gestor.registrar_cambio("item_suelo_agregado", [self._gestor.estado.objetos_suelo, item.instancia_id])
        if item.equipado:
            self._quitar_bonus(item, jugador)
            self._gestor.registrar_cambio("atributo", [item, "equipado", True])
            item.equipado = False

        inv.soltar_por_id(instancia_id)
        self._gestor.estado.objetos_suelo.append(
            ObjetoSuelo(id=item.instancia_id, nombre=item.nombre, tipo_id=item.tipo_id)
        )
        self._bitacora.append(Mensaje("jugador", f"Soltaste {item.nombre}."))
        return ResultadoAccion.exito()

    def equipar(self, instancia_id: str, jugador) -> ResultadoAccion:
        inv = self._gestor.inventario
        if inv is None:
            return ResultadoAccion.fallo("Inventario no inicializado.")

        item = inv.buscar_por_id(instancia_id)
        if item is None:
            return ResultadoAccion.fallo("No tienes ese objeto.")
        if item.clase not in ["arma", "armadura"]:
            return ResultadoAccion.fallo("Ese objeto no es equipable.")

        previos: list = []
        for i in inv.items():
            if i.clase == item.clase:
                previos.append([i.instancia_id, i.equipado])
        seleccion = inv.item_actual()
        self._gestor.registrar_cambio("item_equipado",
                                     [item, inv.posicion_de(instancia_id), previos,
                                      seleccion.instancia_id if seleccion else None])
        self._gestor.registrar_cambio("atributo", [jugador, "ataque", jugador.ataque])
        self._gestor.registrar_cambio("atributo", [jugador, "defensa", jugador.defensa])
        for anterior in inv.items():
            if anterior.clase == item.clase and anterior.equipado:
                jugador.ataque -= anterior.ataque_bonus
                jugador.defensa -= anterior.defensa_bonus
        jugador.ataque += item.ataque_bonus
        jugador.defensa += item.defensa_bonus

        inv.desequipar_clase(item.clase)
        inv.equipar_por_id(instancia_id)
        self._bitacora.append(Mensaje("jugador", f"Equipaste {item.nombre}."))
        return ResultadoAccion.exito()

    def usar(self, instancia_id: str, jugador, simulacion, efectos) -> ResultadoAccion:
        inv = self._gestor.inventario
        item = inv.buscar_por_id(instancia_id) if inv is not None else None
        if item is None:
            return ResultadoAccion.fallo("No tienes ese objeto.")
        resultado = efectos.aplicar_consumible(item, jugador, simulacion)
        if resultado.ok:
            self.consumir(item)
            self._bitacora.append(Mensaje("jugador", resultado.datos))
            return ResultadoAccion.exito()
        return resultado

    def consumir(self, item: ItemInventario) -> None:
        """Retira el consumible, registra su delta y libera su ficha."""
        inv = self._gestor.inventario
        posicion = inv.posicion_de(item.instancia_id)
        self._gestor.registrar_cambio("inventario_quitado", [item, posicion])
        inv.soltar_por_id(item.instancia_id)
        self._servicio.liberar_fichas([item.tipo_id])

    def _quitar_bonus(self, item, jugador) -> None:
        self._gestor.registrar_cambio("atributo", [jugador, "ataque", jugador.ataque])
        self._gestor.registrar_cambio("atributo", [jugador, "defensa", jugador.defensa])
        jugador.ataque -= item.ataque_bonus
        jugador.defensa -= item.defensa_bonus

    #  Recorrido

    def recorrer(self, recorrer, nombre: str, registrar) -> ResultadoAccion:
        """Cambia la selección y la restaura si falla el registro de replay."""
        anterior = self._gestor.inventario.item_actual()
        resultado = recorrer()
        if resultado.ok:
            try:
                registrar(nombre)
            except ErrorRegistro:
                if anterior is not None:
                    self._gestor.inventario.seleccionar(anterior.instancia_id)
                raise
        return resultado

    def siguiente(self) -> ResultadoAccion:
        if self._gestor.inventario is None:
            return ResultadoAccion.fallo("Inventario no inicializado.")
        item = self._gestor.inventario.siguiente()
        if item is None:
            return ResultadoAccion.fallo("Inventario vacío.")
        return ResultadoAccion.exito(datos=item)

    def anterior(self) -> ResultadoAccion:
        if self._gestor.inventario is None:
            return ResultadoAccion.fallo("Inventario no inicializado.")
        item = self._gestor.inventario.anterior()
        if item is None:
            return ResultadoAccion.fallo("Inventario vacío.")
        return ResultadoAccion.exito(datos=item)

    #  Internos

    def _buscar_en_suelo(self, instancia_id: str):
        for o in self._gestor.estado.objetos_suelo:
            if o.id == instancia_id:
                return o
        return None
