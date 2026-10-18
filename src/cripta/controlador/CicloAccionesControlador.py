"""Ejecución reversible de acciones y sincronización de la vista."""

from cripta.dto.Partida_dto import EnemigoPartida
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Mensaje
from cripta.modelo.Combate import esta_vivo
from cripta.replay.reproductor import ErrorRegistro
from cripta.util.Costo_Acciones import costo_accion, calcular_intervalo


class CicloAccionesControlador:
    """Coordina historial, reloj virtual y estado visible.

    Args:
        aplicacion: Contexto compartido de la partida.
    """

    def __init__(self, aplicacion) -> None:
        self._app = aplicacion

    def ejecutar(self, nombre_costo: str, ejecutar, argumento=None) -> ResultadoAccion:
        """Plantilla común de toda acción que consume tiempo.

        1. abre el intervalo del historial,
        2. ejecuta la acción (si falla: no consume tiempo y se descarta el intervalo),
        3. programa la próxima acción del jugador y corre los eventos hasta su turno,
        4. cierra el intervalo y sincroniza el estado para la vista.
        """
        app = self._app
        if not app._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")

        sala_origen = app._jugador.sala
        if app._gestor.historial.hay_intervalo_abierto():
            app._gestor.descartar_intervalo()
        app._gestor.abrir_intervalo()
        historial = app._gestor.historial
        historial.registrar("azar", [app._simulacion.azar, app._simulacion.azar.getstate()])
        for atributo in ["activa", "derrota", "victoria", "terminada"]:
            historial.registrar("atributo",
                               [app._gestor.estado, atributo, getattr(app._gestor.estado, atributo)])
        actual = app._gestor.inventario.item_actual()
        historial.registrar("seleccion_inventario", actual.instancia_id if actual else None)
        try:
            resultado = ejecutar()
            if not resultado.ok:
                historial.revertir_abierto(app._gestor._aplicar_reversion)
                return resultado
            historial.cambiar(app._gestor.estado, "acciones_ejecutadas",
                              app._gestor.estado.acciones_ejecutadas + 1)
            if esta_vivo(app._jugador):
                self.consumir_tiempo(nombre_costo)
            self.finalizar()
            if nombre_costo == "mover":
                app._partida.comprobar_victoria(sala_origen, argumento, app.resumen_red())
            app._partida.registrar_accion(nombre_costo, argumento)
        except Exception as error:
            anteriores = app._tipos_activos()
            historial.revertir_abierto(app._gestor._aplicar_reversion)
            app._avisar(app._cripta_service.reproteger(anteriores, app._tipos_activos()))
            self.finalizar()
            if isinstance(error, ErrorRegistro):
                app._gestor.estado.activa = False
            raise
        app._gestor.cerrar_intervalo()
        if app._gestor.estado.terminada:
            app._partida.guardar_puntaje()
        return resultado

    def consumir_tiempo(self, nombre_costo: str) -> None:
        """Avanza los eventos hasta la siguiente acción del jugador."""
        app = self._app
        sim = app._simulacion
        tiempo_actual = sim.reloj.tiempo_actual
        # Apéndice B: el rastro de la sala actual se refresca en cada acción del jugador.
        app._exploracion.marcar_rastro(tiempo_actual)

        intervalo = calcular_intervalo(costo_accion(nombre_costo), app._jugador.velocidad)
        sim.agenda.reprogramar(app._jugador, tiempo_actual + intervalo, "accion_actor")

        for texto in sim.avanzar_hasta_turno_jugador(app._jugador, app._salas):
            app._bitacora.append(Mensaje("combate", texto))

    def finalizar(self) -> None:
        """Refresca la sala y comprueba la derrota tras los eventos."""
        app = self._app
        app._gestor.estado.sala_actual_id = app._jugador.sala
        app._gestor.refrescar_sala_actual()
        self.sincronizar()
        app._partida.comprobar_derrota(esta_vivo(app._jugador), app.resumen_red())

    def sincronizar(self) -> None:
        """Actualiza los datos que consulta la vista."""
        app = self._app
        estado = app._gestor.estado
        app._actualizar_vecindad()
        app._partida.sincronizar_jugador(app._jugador, app._simulacion)
        estado.rastro = app._exploracion.describir_rastro(estado.reloj_virtual)
        sala_actual = app._salas.obtener(app._jugador.sala)
        if sala_actual is not None:
            estado.enemigos = [
                EnemigoPartida(
                    id=e.identificador, nombre=e.nombre, vida=e.vida, vida_max=e.vida_max,
                    ataque=e.ataque, defensa=e.defensa, velocidad=e.velocidad,
                    comportamiento=e.comportamiento,
                )
                for e in sala_actual.enemigos if esta_vivo(e)
            ]
            # Misma lista (alias): recoger/soltar modifican directamente el suelo de la sala.
            estado.objetos_suelo = sala_actual.objetos
        estado.efectos = app._efectos.describir(app._jugador)
        if app.truco_activo("god_mode"):
            estado.efectos.append("GOD MODE")
        if app.truco_activo("insta_kill"):
            estado.efectos.append("INSTA KILL")
