"""Gestor de la partida activa.

Mantiene el estado mutable del juego, el inventario y el historial de
retroceso. Los controladores especializados (inventario, movimiento,
combate) registran aquí los cambios invertibles.
"""

from __future__ import annotations

from cripta.dto.Partida_dto import (
    EstadoPartida,
    EnemigoPartida,
    ObjetoSuelo,
    SalaModelo,
    SalidaVecina,
    TrampaPartida,
)
from cripta.estructuras.Historial_Retroceso import Historial_Retroceso
from cripta.estructuras.Inventario import Inventario, ItemInventario
from cripta.estructuras.Ordenamientos import ordenar


class GestorPartida:
    """Estado mutable de la partida, inventario e historial."""

    def __init__(self) -> None:
        self.inventario: Inventario | None = None
        self.estado = EstadoPartida()
        self.historial = Historial_Retroceso(max_intervalos=5)

    #  Salas

    def buscar_sala_conocida(self, sala_id: int) -> SalaModelo | None:
        for sala in self.estado.salas_conocidas:
            if sala.id == sala_id:
                return sala
        return None

    def refrescar_sala_actual(self) -> None:
        sala = self.buscar_sala_conocida(self.estado.sala_actual_id)
        if sala is None:
            return

        self.estado.sala_actual_nombre = sala.nombre

        for salida in sala.salidas:
            vecina = self.buscar_sala_conocida(salida.sala_id)
            if vecina is not None:
                salida.nombre = vecina.nombre
            salida.es_salida_final = (salida.sala_id == self.estado.sala_salida_id)

        orden_claves = ["N", "S", "E", "O"]

        def clave_ordenamiento(salida: SalidaVecina) -> int:
            i = 0
            while i < len(orden_claves):
                if orden_claves[i] == salida.direccion:
                    return i
                i += 1
            return 99

        ordenar(sala.salidas, key=clave_ordenamiento)
        self.estado.vecindad = list(sala.salidas)

    #  Inventario

    def reiniciar_inventario(self, capacidad: int) -> None:
        self.inventario = Inventario(capacidad=capacidad)

    #  Historial de retroceso

    def abrir_intervalo(self) -> None:
        self.historial.abrir_intervalo()

    def cerrar_intervalo(self) -> None:
        self.historial.cerrar_intervalo()

    def registrar_cambio(self, etiqueta: str, datos) -> None:
        """Registra un cambio invertible en el intervalo abierto.

        Args:
            etiqueta: Nombre del cambio.
            datos: Información necesaria para invertirlo.
        """
        self.historial.registrar(etiqueta, datos)

    def deshacer(self) -> bool:
        """Aplica la inversión del intervalo más reciente.

        Returns:
            True si se invirtió algo, False si no había nada.
        """
        return self.historial.deshacer(self._aplicar_reversion)

    def _aplicar_reversion(self, etiqueta: str, datos) -> None:
        if etiqueta == "inventario_agregado":
            self._revertir_inventario_agregado(datos)
        elif etiqueta == "inventario_quitado":
            self._revertir_inventario_quitado(datos)
        elif etiqueta == "item_equipado":
            self._revertir_item_equipado(datos)
        elif etiqueta == "item_suelo_agregado":
            self._revertir_suelo_agregado(datos)
        elif etiqueta == "item_suelo_quitado":
            self._revertir_suelo_quitado(datos)
        # TODO: Otras etiquetas (vida, reloj, rastro, puertas, efectos, eventos)

    #  Reversiones de inventario

    def _revertir_inventario_agregado(self, datos) -> None:
        """El item se había agregado; hay que quitarlo.

        Args:
            datos: Item que se agregó, con su instancia_id.
        """
        item = datos
        if self.inventario is not None:
            self.inventario.soltar_por_id(item.instancia_id)

    def _revertir_inventario_quitado(self, datos) -> None:
        """El item se había quitado; hay que reinsertarlo.

        Args:
            datos: (item, posición relativa al frente).
        """
        item, posicion = datos
        if self.inventario is not None:
            self.inventario.reinsertar_en(item, posicion)

    def _revertir_item_equipado(self, datos) -> None:
        """El item se había equipado; hay que restaurar el estado previo.

        Args:
            datos: Lista de (instancia_id, estaba_equipado_antes).
        """
        if self.inventario is None:
            return
        for instancia_id, estaba_equipado in datos:
            item = self.inventario.buscar_por_id(instancia_id)
            if item is not None:
                item.equipado = estaba_equipado

    def _revertir_suelo_agregado(self, datos) -> None:
        """Se había agregado un objeto al suelo; hay que quitarlo.

        Args:
            datos: instancia_id del objeto agregado.
        """
        instancia_id = datos
        self.estado.objetos_suelo = [
            o for o in self.estado.objetos_suelo if o.id != instancia_id
        ]

    def _revertir_suelo_quitado(self, datos) -> None:
        """Se había quitado un objeto del suelo; hay que reinsertarlo.

        Args:
            datos: (objeto, posición en el suelo).
        """
        obj, posicion = datos
        self.estado.objetos_suelo.insert(posicion, obj)