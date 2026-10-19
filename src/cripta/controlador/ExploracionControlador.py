"""
Responsabilidades:
    - Ensamblado de salas: crea todas las salas (vacías) desde el esqueleto y les
      incorpora el contenido que llega de la red, por lotes (4.2).
    - Movimiento entre salas (2.3).
    - Apertura de puertas con llave y cierre automático (2.5, 2.10).
    - Rastro: marca el instante de la última visita de cada sala (2.9, Apéndice B).
    - Vecindad: copia el estado vivo de las puertas y de las salas vecinas al DTO
      que lee la Vista.

Este controlador es el dueño del índice de salas. La plantilla común de una acción del
jugador (transacción, historial, tiempo, replay) sigue en `Aplicacion`, que se le pasa
como contexto porque el jugador y la simulación se recrean en cada partida.

Complejidad:
    mover / abrir: O(1) sobre la sala actual (máx. 4 salidas) más el costo del ciclo
    actualizar_vecindad: O(k * e), k = salidas (máx. 4), e = enemigos de la vecina
"""

from __future__ import annotations

from cripta.dto.Partida_dto import ContenidoSala, SalaModelo
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Mensaje
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Salidas import Salidas
from cripta.modelo.Combate import esta_vivo
from cripta.modelo.Puertas import abrir_salida, buscar_llave
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.enemigos.Rastreador import DURACION_RASTRO


class ExploracionControlador:
    def __init__(self, app) -> None:
        self._app = app
        self.salas: IndiceSalas = IndiceSalas()
        self.max_id_sala = 0

    # Accesos cortos al contexto (se leen siempre de la aplicación: cambian por partida)

    @property
    def _gestor(self):
        return self._app._gestor

    @property
    def _bitacora(self):
        return self._app._bitacora

    @property
    def _servicio(self):
        return self._app._cripta_service

    @property
    def _jugador(self):
        return self._app._jugador

    @property
    def _simulacion(self):
        return self._app._simulacion

    @property
    def _estado(self):
        return self._app._gestor.estado

    #  Ensamblado de salas (4.2)

    def ensamblar_salas(self, esqueleto: list[SalaModelo]) -> None:
        """Crea TODAS las salas (vacías) apenas llega el esqueleto.

        Así un enemigo activo puede moverse a una sala cuyo contenido aún no
        se pidió, y el rastreador puede consultar el rastro de cualquier vecina.
        """
        self.salas = IndiceSalas()
        self.max_id_sala = 0
        for sala_modelo in esqueleto:
            salidas = Salidas()
            for v in sala_modelo.salidas:
                salidas.agregar(v.direccion, v.sala_id, v.cerrada, v.llave or None, v.cierre_automatico)
            self.salas.insertar(sala_modelo.id, SalaJuego(
                id=sala_modelo.id, nombre=sala_modelo.nombre, salidas=salidas,
                enemigos=[], objetos=[], trampas=[],
            ))
            if sala_modelo.id > self.max_id_sala:
                self.max_id_sala = sala_modelo.id

    def cargar_lote(self, origen_id: int) -> None:
        """Lote de hasta 10 salas alrededor de `origen_id` (la precarga vive en CriptaService)."""
        self._servicio.cargar_lote(self._estado.cripta_id, self.salas, self.max_id_sala,
                                   origen_id, self.incorporar_contenido)

    def incorporar_contenido(self, sala: SalaJuego | None, contenido: ContenidoSala) -> None:
        """Incorporar NO activa enemigos (2.4): quedan dormidos hasta que el jugador entre."""
        if sala is None or sala.contenido_cargado:
            return  # una sala ya cargada no se vuelve a incorporar
        for dto in contenido.enemigos:
            # agregar (no reemplazar): puede haber enemigos activos que ya llegaron caminando
            sala.agregar_enemigo(self._app._combate.crear_enemigo(dto, sala.id))
        sala.objetos.extend(contenido.objetos)
        for t in contenido.trampas:
            sala.trampas.append(self._app._efectos.crear_trampa(t))
        sala.contenido_cargado = True
        self._estado.contenido_cargado.append(sala.id)

    #  Rastro (2.9, Apéndice B)

    def marcar_rastro(self, tiempo_actual: int) -> None:
        """El rastro de la sala actual se refresca en cada acción del jugador."""
        sala = self.salas.obtener(self._jugador.sala)
        self._simulacion.agenda.cambiar(sala, "ultimo_tiempo_visita", tiempo_actual)

    def describir_rastro(self, tiempo_actual: int) -> list[str]:
        """Describe únicamente las huellas propias, sin consultar enemigos ocultos."""
        lineas = [f"RASTRO: cada acción renueva la marca de tu sala durante {DURACION_RASTRO} u.t.",
                  "El tiempo es virtual: leer este panel no consume rastro."]
        for sala in self.salas._datos:
            if sala is None or sala.ultimo_tiempo_visita is None:
                continue
            antiguedad = tiempo_actual - sala.ultimo_tiempo_visita
            restante = max(0, DURACION_RASTRO - antiguedad)
            estado = f"rastreable {restante} u.t. más" if restante else "rastro vencido"
            lineas.append(f"Sala {sala.id}: marca t={sala.ultimo_tiempo_visita} · "
                          f"antigüedad {antiguedad} u.t. · {estado}.")
        return lineas

    #  Vecindad

    def actualizar_vecindad(self) -> None:

        sala = self.salas.obtener(self._jugador.sala)
        if sala is None:
            return
        for v in self._estado.vecindad:
            salida = sala.salidas.obtener(v.direccion)
            if salida is not None:
                v.cerrada = salida.cerrada
                v.transitable = not salida.cerrada
                v.llave = salida.llave or ""
                v.cierre_automatico = salida.cierre_automatico
            vecina = self.salas.obtener(v.sala_id)
            if vecina is None:
                continue
            hay_enemigos = False
            for e in vecina.enemigos:
                if esta_vivo(e):
                    hay_enemigos = True
                    break
            v.tiene_enemigos = hay_enemigos
            v.tiene_objetos = len(vecina.objetos) > 0

    #  Movimiento (2.3)

    def preparar_movimiento(self, direccion: str) -> None:
        """Carga el destino sin mover al jugador ni avanzar el reloj virtual."""
        actual = self.salas.obtener(self._jugador.sala)
        salida = actual.salidas.obtener(direccion) if actual else None
        if salida is None or salida.cerrada:
            return
        error = self._servicio.asegurar_sala_cargada(
            self._estado.cripta_id, self.salas, self.max_id_sala,
            salida.sala_destino, self.incorporar_contenido)
        if error is not None:
            raise RuntimeError(f"No se pudo cargar la sala destino: {error}")

    def mover(self, direccion: str) -> ResultadoAccion:
        app = self._app
        if not app._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")

        direccion = direccion.strip().upper()
        sala_actual = self.salas.obtener(self._jugador.sala)
        if sala_actual is None:
            return ResultadoAccion.fallo("Sala actual no cargada.")

        salida = sala_actual.salidas.obtener(direccion)
        if salida is None:
            return ResultadoAccion.fallo("No hay salida en esa dirección.")
        if salida.cerrada:
            return ResultadoAccion.fallo("La puerta está cerrada.")

        destino_id = salida.sala_destino
        # 4.2: el contenido debe estar ANTES de confirmar el movimiento.
        error = self._servicio.asegurar_sala_cargada(
            self._estado.cripta_id, self.salas, self.max_id_sala, destino_id,
            self.incorporar_contenido)
        if error is not None:
            return ResultadoAccion.fallo(f"No se pudo cargar la sala destino: {error}")

        destino = self.salas.obtener(destino_id)
        tipos = self._servicio.tipos_activos(self._gestor.inventario, self.salas, destino)
        tipos.extend(e.tipo for e in destino.enemigos if e.vida > 0 and e._proximo_evento is None)
        try:
            self._servicio.validar_capacidad(tipos)
        except RuntimeError as error:
            return ResultadoAccion.fallo(str(error))

        resultado = app._accion_jugador(
            "mover", lambda: self._ejecutar_movimiento(destino_id, direccion), direccion)
        if resultado.ok and app._partida_en_curso():
            app._avisar(self._servicio.precargar_alrededor(   # lista para la próxima puerta
                self._estado.cripta_id, self.salas, self.max_id_sala,
                self._jugador.sala, self.incorporar_contenido))
        return resultado

    def _ejecutar_movimiento(self, destino_id: int, direccion: str) -> ResultadoAccion:
        app = self._app
        sala_origen = self.salas.obtener(self._jugador.sala)
        sala_destino = self.salas.obtener(destino_id)
        tiempo_actual = self._simulacion.reloj.tiempo_actual

        self._servicio.liberar_contenido_visible(sala_origen)   # deja de ser la sala actual
        self._simulacion.agenda.cambiar(self._jugador, "sala", destino_id)
        self._simulacion.agenda.cambiar(sala_destino, "ultimo_tiempo_visita", tiempo_actual)  # 2.9
        app._combate.activar_sala(sala_destino, self._simulacion)   # 2.4
        self._servicio.fijar_fichas(self._servicio.tipos_visibles(sala_destino))
        self._estado.objetos_suelo = sala_destino.objetos
        self._bitacora.append(Mensaje("jugador", f"Te mueves al {direccion}: {sala_destino.nombre}."))
        marca = sala_origen.ultimo_tiempo_visita
        if marca is not None:
            restante = max(0, DURACION_RASTRO - (tiempo_actual - marca))
            self._bitacora.append(Mensaje("rastro", f"Dejaste una marca en sala {sala_origen.id} "
                                          f"en t={marca}: rastreable {restante} u.t. más."))

        # 2.10: cada trampa armada se activa al entrar, antes del siguiente evento.
        app._efectos.disparar_trampas(sala_destino, self._jugador, self._simulacion)
        return ResultadoAccion.exito()

    #  Puertas (2.5)

    def abrir(self, direccion: str) -> ResultadoAccion:
        """Abre la puerta de la sala actual en `direccion`. Costo 50 (abrir_puerta)."""
        direccion = direccion.strip().upper()
        return self._app._accion_jugador(
            "abrir_puerta", lambda: self._ejecutar_apertura(direccion), direccion)

    def _ejecutar_apertura(self, direccion: str) -> ResultadoAccion:
        sala = self.salas.obtener(self._jugador.sala)
        if sala is None:
            return ResultadoAccion.fallo("Sala actual no cargada.")
        salida = sala.salidas.obtener(direccion)
        if salida is None:
            return ResultadoAccion.fallo("No hay salida en esa dirección.")
        if not salida.cerrada:
            return ResultadoAccion.fallo("Esa puerta ya está abierta.")
        if not salida.llave:
            return ResultadoAccion.fallo("Esa puerta no se abre con llave.")
        inventario = self._gestor.inventario
        llave = buscar_llave(inventario.items(), salida.llave) if inventario is not None else None
        if llave is None:
            return ResultadoAccion.fallo("No tienes la llave correcta.")

        tiempo = self._simulacion.reloj.tiempo_actual
        abrir_salida(salida, tiempo, self._simulacion.agenda)   # incluye el cierre automático
        self._comunicar_acceso_salida(sala.id, salida)
        self._bitacora.append(Mensaje("jugador", f"Abres la puerta {direccion} con {llave.nombre}."))
        return ResultadoAccion.exito()

    def _comunicar_acceso_salida(self, sala_id: int, salida) -> None:
        """Avisa a victoria si esta puerta es el acceso válido a la sala de salida.

        PartidaControlador lo anota solo si la puerta lleva a la sala de salida y se abrió
        con la llave de la salida; lo registra en el historial, así que el pergamino de
        retroceso también lo deshace.
        """
        self._app._partida.registrar_apertura_salida(sala_id, salida)
