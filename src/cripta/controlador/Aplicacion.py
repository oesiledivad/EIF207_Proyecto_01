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
    EnemigoPartida
)
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.servicio.CriptaService import CriptaService
from cripta.modelo.Simulacion import Simulacion
from cripta.modelo.Combate import esta_vivo, calcular_danio, aplicar_danio, procesar_muerte
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.enemigos.Guardian import Guardian
from cripta.modelo.enemigos.Errante import Errante
from cripta.modelo.enemigos.Rastreador import Rastreador
from cripta.util.Costo_Acciones import COSTOS, calcular_intervalo

# esto me arregla el problema de no poder utilizar dict ni sorted
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Salidas import Salidas
from cripta.estructuras.Ordenamientos import ordenar
from cripta.modelo.Trampa import TrampaJuego

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
        self._simulacion: Simulacion | None = None
        self._jugador: Jugador | None = None
        self._salas: IndiceSalas = IndiceSalas()  # antes: dict[int, SalaJuego]

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

        self._simulacion = Simulacion(semilla_efectiva)
        self._jugador = Jugador(
            identificador="jugador", vida=detalles.jugador_vida_max, vida_max=detalles.jugador_vida_max,
            ataque=detalles.jugador_ataque, defensa=detalles.jugador_defensa,
            velocidad=detalles.jugador_velocidad, sala=detalles.sala_inicial,
            tiempo_siguiente=0, inventario_max=detalles.inventario_max,
        )
        evento_inicial = self._simulacion.agenda.insertar(0, self._jugador, "accion_actor")
        self._jugador._proximo_evento = evento_inicial

        self._construir_sala(detalles.sala_inicial)
        self._activar_sala(detalles.sala_inicial)
        self._salas.obtener(detalles.sala_inicial).ultimo_tiempo_visita = 0

        return ResultadoInicio(ok=True, semilla_efectiva=semilla_efectiva)

    def _construir_sala(self, sala_id: int) -> SalaJuego:
        assert self._simulacion is not None
        if self._salas.contiene(sala_id):
            return self._salas.obtener(sala_id)

        sala_modelo = self._gestor.buscar_sala_conocida(sala_id)
        if sala_modelo is None:
            raise ValueError(f"Sala {sala_id} no está en el esqueleto cargado.")

        contenido = self._cripta_service.cargar_contenido_sala(self._gestor.estado.cripta_id, sala_id)
        enemigos = [self._crear_enemigo(dto, sala_id) for dto in contenido.enemigos]

        self._cripta_service.asegurar_fichas([t.tipo for t in contenido.trampas])
        trampas = []
        for t in contenido.trampas:
            ficha = self._cripta_service.obtener_ficha(t.tipo)
            trampas.append(TrampaJuego(
                instancia=t.id, armada=t.activa,
                dano=ficha.daño if ficha else 0,
                rearme=ficha.rearme if ficha else 300,
            ))

        salidas = Salidas()
        for v in sala_modelo.salidas:
            salidas.agregar(v.direccion, v.sala_id, v.cerrada)

        sala_juego = SalaJuego(
            id=sala_id, nombre=sala_modelo.nombre, salidas=salidas,
            enemigos=enemigos, objetos=contenido.objetos, trampas=trampas,
        )
        self._salas.insertar(sala_id, sala_juego)
        return sala_juego

    def _activar_sala(self, sala_id: int) -> None:
        sala = self._salas.obtener(sala_id)
        enemigos_ordenados = ordenar(sala.enemigos, key=lambda e: e.identificador)
        for enemigo in enemigos_ordenados:
            if enemigo._proximo_evento is None:
                self._activar_enemigo(enemigo)

    def _crear_enemigo(self, dto: EnemigoPartida, sala_id: int):
        match dto.comportamiento:
            case "guardián":
                clase = Guardian
            case "errante":
                clase = Errante
            case "rastreador":
                clase = Rastreador
            case otro:
                raise ValueError(f"Comportamiento desconocido: {otro}")
        return clase(
            identificador=dto.id, vida=dto.vida, vida_max=dto.vida_max or dto.vida,
            ataque=dto.ataque, defensa=dto.defensa, velocidad=dto.velocidad,
            sala=sala_id, tiempo_siguiente=None, comportamiento=dto.comportamiento,
        )

    def _activar_enemigo(self, enemigo) -> None:
        tiempo_actual = self._simulacion.reloj.tiempo_actual
        intervalo = calcular_intervalo(COSTOS["esperar"], enemigo.velocidad)
        evento = self._simulacion.agenda.insertar(tiempo_actual + intervalo, enemigo, "accion_actor")
        enemigo._proximo_evento = evento

    def _sincronizar_estado(self) -> None:
        estado = self._gestor.estado
        estado.reloj_virtual = self._simulacion.reloj.tiempo_actual
        estado.jugador_vida = self._jugador.vida
        sala_actual = self._salas.obtener(self._jugador.sala)
        if sala_actual is not None:
            estado.enemigos = [
                EnemigoPartida(
                    id=e.identificador, nombre=e.identificador, vida=e.vida, vida_max=e.vida_max,
                    ataque=e.ataque, defensa=e.defensa, velocidad=e.velocidad,
                    comportamiento=e.comportamiento,
                )
                for e in sala_actual.enemigos if esta_vivo(e)
            ]

    # ---- acción: esperar ----

    def esperar(self) -> ResultadoAccion:
        if self._simulacion is None or self._jugador is None:
            return ResultadoAccion.fallo("La partida no está activa.")

        tiempo_actual = self._simulacion.reloj.tiempo_actual
        intervalo = calcular_intervalo(COSTOS["esperar"], self._jugador.velocidad)
        self._simulacion.agenda.reprogramar(self._jugador, tiempo_actual + intervalo, "accion_actor")
        self._bitacora.append(Mensaje("jugador", "Esperás."))

        mensajes = self._simulacion.avanzar_hasta_turno_jugador(self._jugador, self._salas)
        for texto in mensajes:
            self._bitacora.append(Mensaje("combate", texto))

        self._sincronizar_estado()
        if not esta_vivo(self._jugador):
            self._gestor.estado.derrota = True
            self._gestor.estado.activa = False

        return ResultadoAccion.exito()

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
        if self._simulacion is None or self._jugador is None:
            return ResultadoAccion.fallo("La partida no está activa.")

        direccion = direccion.strip().upper()
        sala_actual = self._salas.obtener(self._jugador.sala)
        if sala_actual is None:
            return ResultadoAccion.fallo("Sala actual no cargada.")

        salida = sala_actual.salidas.obtener(direccion)
        if salida is None:
            return ResultadoAccion.fallo("No hay salida en esa dirección.")
        if salida.cerrada:
            return ResultadoAccion.fallo("La puerta está cerrada.")

        destino_id = salida.sala_destino
        self._construir_sala(destino_id)  # §4.2
        self._activar_sala(destino_id)  # §2.4

        tiempo_actual = self._simulacion.reloj.tiempo_actual
        self._jugador.sala = destino_id
        sala_destino = self._salas.obtener(destino_id)
        sala_destino.ultimo_tiempo_visita = tiempo_actual  # §2.9

        trampa_armada = next((t for t in sala_destino.trampas if t.armada), None)
        if trampa_armada is not None:
            from cripta.modelo.Efectos import disparar_trampa
            texto = disparar_trampa(trampa_armada, self._jugador, tiempo_actual, self._simulacion.agenda)
            self._bitacora.append(Mensaje("combate", texto))
            if not esta_vivo(self._jugador):
                self._gestor.estado.derrota = True
                self._gestor.estado.activa = False
                self._sincronizar_estado()
                return ResultadoAccion.exito()

        intervalo = calcular_intervalo(COSTOS["mover"], self._jugador.velocidad)
        self._simulacion.agenda.reprogramar(self._jugador, tiempo_actual + intervalo, "accion_actor")
        self._bitacora.append(Mensaje("jugador", f"Te mueves al {direccion}."))

        mensajes = self._simulacion.avanzar_hasta_turno_jugador(self._jugador, self._salas)
        for texto in mensajes:
            self._bitacora.append(Mensaje("combate", texto))

        self._gestor.estado.sala_actual_id = destino_id
        self._gestor.refrescar_sala_actual()
        self._sincronizar_estado()

        if not esta_vivo(self._jugador):
            self._gestor.estado.derrota = True
            self._gestor.estado.activa = False

        return ResultadoAccion.exito()

    def atacar(self, instancia_id: str) -> ResultadoAccion:
        if self._simulacion is None or self._jugador is None:
            return ResultadoAccion.fallo("La partida no está activa.")

        sala_actual = self._salas.obtener(self._jugador.sala)
        if sala_actual is None:
            return ResultadoAccion.fallo("Sala actual no cargada.")

        enemigo = next(
            (e for e in sala_actual.enemigos if e.identificador == instancia_id and esta_vivo(e)),
            None,
        )
        if enemigo is None:
            return ResultadoAccion.fallo("Ese enemigo no está aquí.")

        tiempo_actual = self._simulacion.reloj.tiempo_actual
        dano = calcular_danio(self._jugador, enemigo, self._simulacion.azar)
        aplicar_danio(enemigo, dano)
        self._bitacora.append(Mensaje("combate", f"Atacás a {enemigo.identificador} por {dano}."))

        if not esta_vivo(enemigo):
            self._bitacora.append(Mensaje("combate", f"{enemigo.identificador} muere."))
            procesar_muerte(enemigo, self._simulacion.agenda)

        intervalo = calcular_intervalo(COSTOS["atacar"], self._jugador.velocidad)
        self._simulacion.agenda.reprogramar(self._jugador, tiempo_actual + intervalo, "accion_actor")

        mensajes = self._simulacion.avanzar_hasta_turno_jugador(self._jugador, self._salas)
        for texto in mensajes:
            self._bitacora.append(Mensaje("combate", texto))

        self._sincronizar_estado()
        if not esta_vivo(self._jugador):
            self._gestor.estado.derrota = True
            self._gestor.estado.activa = False

        return ResultadoAccion.exito()

    def terminar(self) -> None:
        self._gestor.estado.activa = False
        self._gestor.estado.terminada = True