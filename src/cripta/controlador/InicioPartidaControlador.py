"""Preparación de partidas y de su registro."""

from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.dto.Partida_dto import ResultadoInicio
from cripta.estructuras.Bitacora import Mensaje


class InicioPartidaControlador:
    """Coordina la carga inicial de datos, actores y replay.

    Args:
        aplicacion: Contexto compartido de la partida.
    """

    def __init__(self, aplicacion) -> None:
        self._app = aplicacion

    def preparar_seleccion(self):
        """Cierra la sesión y renueva su presupuesto antes de consultar otras criptas."""
        app = self._app
        app.terminar()
        app._cripta_service.reiniciar_partida()
        app._jugador = None
        app._simulacion = None

    def iniciar(
        self,
        nombre_jugador: str,
        semilla: str,
        cripta_id: str,
        registrar: bool = True,
    ) -> ResultadoInicio:
        """Prepara una partida nueva; una carga solicita registrar=False para omitir replay."""
        app = self._app
        try:
            nombre, semilla_efectiva = app._partida.validar_inicio(nombre_jugador, semilla, cripta_id)
        except ValueError as error:
            return ResultadoInicio(ok=False, motivo=str(error))
        if registrar:
            app._partida.reanudar_registro()
        else:
            app._partida.suspender_registro()

        if app._jugador is not None:
            app._cripta_service.reiniciar_partida()
        try:
            # Si ya se pidió al previsualizar, el servicio lo devuelve sin gastar red.
            detalles = app._cripta_service.obtener_detalles(cripta_id)
        except (PresupuestoAgotado, RuntimeError) as e:
            return ResultadoInicio(ok=False, motivo=f"No se pudieron leer los datos de la cripta: {e}")
        app._cripta_service.fijar_presupuesto(detalles.presupuesto_solicitudes)
        if app._partida.registro is not None:
            try:
                app._cripta_service.obtener_version_catalogo(actualizar=True)
            except (OSError, RuntimeError, ValueError, NotImplementedError) as error:
                return ResultadoInicio(ok=False, motivo=f"No se pudo preparar el registro: {error}")

        app._partida.iniciar(
            detalles, nombre, semilla_efectiva,
            "offline" if app._cripta_service.es_offline() else "red",
        )

        app._bitacora.limpiar()
        app._guardado.actual = None
        app._bitacora.append(Mensaje("sistema", f"Partida iniciada en {cripta_id}."))
        app._bitacora.append(Mensaje("sistema", f"Semilla: {semilla_efectiva}."))
        # §4.4: validar lo persistido ANTES de cargar esqueleto, contenido o fichas.
        app._bitacora.append(Mensaje("sistema", app._cripta_service.preparar_persistencia(detalles)))

        app._jugador, app._simulacion = app._partida.preparar_actores(detalles, semilla_efectiva)

        try:
            esqueleto = app._cripta_service.cargar_esqueleto_salas(cripta_id, detalles.sala_salida)
            app._gestor.estado.salas_conocidas = esqueleto
            app._crear_salas_desde_esqueleto(esqueleto)
            # §2.4: el contenido de la sala inicial debe estar antes de la primera acción.
            # Se pide en el mismo lote que las salas más cercanas (hasta 10).
            app._cargar_lote(detalles.sala_inicial)
        except (PresupuestoAgotado, RuntimeError, ValueError) as e:
            app._gestor.estado.activa = False
            return ResultadoInicio(ok=False, motivo=f"No se pudo cargar la cripta: {e}")

        sala_inicial = app._salas.obtener(detalles.sala_inicial)
        if sala_inicial is None or not sala_inicial.contenido_cargado:
            app._gestor.estado.activa = False
            return ResultadoInicio(ok=False, motivo="No se pudo cargar la cripta: el contenido de la "
                                                    "sala inicial no está disponible.")
        sala_inicial.ultimo_tiempo_visita = 0             # §2.9
        try:
            tipos = app._cripta_service.tipos_visibles(sala_inicial)
            tipos.extend(e.tipo for e in sala_inicial.enemigos if e.vida > 0)
            app._cripta_service.validar_capacidad(tipos)
            app._combate.activar_sala(sala_inicial, app._simulacion)
            app._cripta_service.fijar_fichas(app._cripta_service.tipos_visibles(sala_inicial))
        except (RuntimeError, OSError, ValueError) as error:
            app._gestor.estado.activa = False
            return ResultadoInicio(ok=False, motivo=f"No se pudo preparar la sala inicial: {error}")
        app._gestor.refrescar_sala_actual()
        app._sincronizar_estado()

        if app._partida.registro is not None:
            try:
                app._partida.iniciar_registro(
                    detalles, app._cripta_service.obtener_version_catalogo(),
                    semilla_efectiva, nombre, app._cripta_service._cache_fichas.capacidad,
                )
            except OSError as error:
                app._gestor.estado.activa = False
                return ResultadoInicio(ok=False, motivo=f"No se pudo crear el registro: {error}")
        return ResultadoInicio(ok=True, semilla_efectiva=semilla_efectiva)
