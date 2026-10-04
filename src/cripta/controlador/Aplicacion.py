"""Controlador de Aplicación (MVC).
"""

from __future__ import annotations

import random

from cripta.adaptadores.Crypt_Data_Source import CryptDataSource
from cripta.controlador.GestorPartida import GestorPartida
from cripta.controlador.InventarioControlador import InventarioControlador
from cripta.dto.Partida_dto import (
    CriptaResumen,
    DetallesCripta,
    EstadoPartida,
    ResultadoInicio,
    ContenidoSala,
)
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.servicio.CriptaService import CriptaService

def _generar_semilla() -> int:
    return random.SystemRandom().randint(1, 2**31 - 1)

class Aplicacion:
    """Controlador de Aplicación.

    Args:
        data_source: Adaptador de datos (red u offline).
    """

    def __init__(self, data_source: CryptDataSource) -> None:
        self._cripta_service = CriptaService(data_source)
        self._gestor = GestorPartida()
        self._bitacora = Bitacora(capacidad=20)
        self._inventario = InventarioControlador(self._gestor, self._bitacora)

    #  Selección

    def listar_criptas(self) -> list[CriptaResumen]:
        return self._cripta_service.listar_criptas()

    def previsualizar_cripta(self, cripta_id: str) -> DetallesCripta:
        return self._cripta_service.obtener_detalles(cripta_id)

    def iniciar_partida(
        self,
        nombre_jugador: str,
        semilla: str,
        cripta_id: str,
    ) -> ResultadoInicio:
        nombre = nombre_jugador.strip()
        if not nombre:
            return ResultadoInicio(
                ok=False,
                motivo="El nombre del jugador no puede estar vacío.",
            )
        if not cripta_id:
            return ResultadoInicio(
                ok=False,
                motivo="Debes seleccionar una cripta.",
            )

        semilla_txt = semilla.strip()
        if semilla_txt:
            if not semilla_txt.isdigit():
                return ResultadoInicio(
                    ok=False,
                    motivo="La semilla debe ser un número entero o quedar vacía.",
                )
            semilla_efectiva = int(semilla_txt)
        else:
            semilla_efectiva = _generar_semilla()

        detalles = self._cripta_service.obtener_detalles(cripta_id)

        self._gestor.estado = EstadoPartida(
            activa=True,
            nombre_jugador=nombre,
            cripta_id=detalles.id,
            version_cripta=detalles.version,
            semilla=semilla_efectiva,
            modo="offline" if self._cripta_service.es_offline() else "red",
            presupuesto_solicitudes=detalles.presupuesto_solicitudes,
            inventario_max=detalles.inventario_max,
            sala_actual_id=detalles.sala_inicial,
            sala_actual_nombre="(cargando...)",
            sala_salida_id=detalles.sala_salida,
            llave_salida=detalles.llave_salida,
            jugador_vida=detalles.jugador_vida_max,
            jugador_vida_max=detalles.jugador_vida_max,
            jugador_ataque=detalles.jugador_ataque,
            jugador_defensa=detalles.jugador_defensa,
            jugador_velocidad=detalles.jugador_velocidad,
        )

        self._gestor.reiniciar_inventario(detalles.inventario_max)

        self._bitacora.limpiar()
        self._bitacora.append(Mensaje("sistema", f"Partida iniciada en {cripta_id}."))
        self._bitacora.append(Mensaje("sistema", f"Semilla: {semilla_efectiva}."))

        self._gestor.estado.salas_conocidas = (
            self._cripta_service.cargar_esqueleto_salas(
                cripta_id, detalles.sala_salida
            )
        )
        self._gestor.refrescar_sala_actual()

        contenido: ContenidoSala = self._cripta_service.cargar_contenido_sala(
            cripta_id, detalles.sala_inicial
        )
        self._gestor.estado.enemigos = contenido.enemigos
        self._gestor.estado.objetos_suelo = contenido.objetos
        self._gestor.estado.trampas = contenido.trampas
        self._gestor.estado.contenido_cargado.append(detalles.sala_inicial)

        return ResultadoInicio(ok=True, semilla_efectiva=semilla_efectiva)

    #  Consultas de juego

    def estado_partida(self) -> EstadoPartida:
        return self._gestor.estado

    def bitacora(self) -> Bitacora:
        return self._bitacora

    def solicitudes_usadas(self) -> int:
        return self._cripta_service.requests_made

    #  Inventario (delegado a InventarioController)

    def recoger(self, instancia_id: str) -> ResultadoAccion:
        return self._inventario.recoger(instancia_id)

    def soltar(self, instancia_id: str) -> ResultadoAccion:
        return self._inventario.soltar(instancia_id)

    def equipar(self, instancia_id: str) -> ResultadoAccion:
        return self._inventario.equipar(instancia_id)

    def usar(self, instancia_id: str) -> ResultadoAccion:
        return self._inventario.usar(instancia_id)

    def usar_pergamino(self) -> ResultadoAccion:
        return self._inventario.usar_pergamino()

    def siguiente_item(self) -> ResultadoAccion:
        return self._inventario.siguiente()

    def anterior_item(self) -> ResultadoAccion:
        return self._inventario.anterior()

    def vista_inventario(self, criterio: str) -> list:
        return self._inventario.vista_ordenada(criterio)

    def inventario(self):
        """Devuelve el inventario activo o None."""
        return self._gestor.inventario

    #  Acciones de partida

    def mover(self, direccion: str) -> ResultadoAccion:
        self._bitacora.append(
            Mensaje("sistema", f"Mover {direccion} aún no implementado.")
        )
        return ResultadoAccion.fallo("Movimiento aún no implementado.")

    def atacar(self, instancia_id: str) -> ResultadoAccion:
        self._bitacora.append(Mensaje("sistema", "Ataque aún no implementado."))
        return ResultadoAccion.fallo("Ataque aún no implementado.")

    def esperar(self) -> ResultadoAccion:
        self._bitacora.append(Mensaje("sistema", "Espera aún no implementada."))
        return ResultadoAccion.fallo("Espera aún no implementada.")

    def terminar(self) -> None:
        self._gestor.estado.activa = False
        self._gestor.estado.terminada = True