"""Registro, retroceso y cierre de la partida; no ejecuta el ciclo de simulación."""
import random
from uuid import uuid4

from cripta.modelo.Jugador import Jugador
from cripta.modelo.Simulacion import Simulacion

from cripta.adaptadores.Puntajes import Puntaje, TablaPuntajes
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.dto.Partida_dto import EstadoPartida
from cripta.estructuras.Bitacora import Mensaje
from cripta.replay.reproductor import Cabecera, RegistroPartida, ErrorRegistro


class PartidaControlador:
    def __init__(self, gestor, bitacora, carpeta_logs=None, ruta_puntajes=None):
        self._gestor = gestor
        self._bitacora = bitacora
        self._registro = RegistroPartida(carpeta_logs) if carpeta_logs is not None else None
        self._registro_suspendido = None
        if ruta_puntajes is None and self._registro is not None:
            ruta_puntajes = self._registro.carpeta / "puntajes.json"
        self._puntajes = TablaPuntajes(ruta_puntajes) if ruta_puntajes is not None else None
        self._partida_id = None
        self._puntaje_guardado = False
        self.error_puntaje = ""
        self._salidas_abiertas = []
        self.trucos_activos = False

    @property
    def identificador(self):
        """Devuelve la identidad estable de la partida para sus archivos."""
        return self._partida_id

    def suspender_registro(self):
        """Aparta el replay para cargas o cheats hasta una nueva partida normal."""
        if self._registro is not None:
            self._registro_suspendido = self._registro
            self._registro = None

    def reanudar_registro(self):
        """Recupera el registro configurado para comenzar una partida normal."""
        if self._registro_suspendido is not None:
            self._registro = self._registro_suspendido
            self._registro_suspendido = None

    @property
    def registro(self):
        return self._registro

    def reiniciar(self):
        self.trucos_activos = False
        self._partida_id = uuid4().hex
        self._puntaje_guardado = False
        self.error_puntaje = ""
        self._salidas_abiertas = []
        self._gestor.historial.limpiar()

    @staticmethod
    def validar_inicio(nombre: str, semilla: str, cripta_id: str) -> list:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre del jugador no puede estar vacío.")
        if not cripta_id:
            raise ValueError("Debes seleccionar una cripta.")
        semilla = semilla.strip()
        if not semilla:
            return [nombre, random.SystemRandom().randint(1, 2**31 - 1)]
        if not semilla.isdecimal():
            raise ValueError("La semilla debe ser un número entero o quedar vacía.")
        try:
            return [nombre, int(semilla)]
        except ValueError as error:
            raise ValueError("La semilla debe ser un número entero válido.") from error

    def preparar_actores(self, detalles, semilla: int):
        simulacion = Simulacion(semilla, self._gestor.historial)
        jugador = Jugador(
            identificador="jugador", vida=detalles.jugador_vida_max, vida_max=detalles.jugador_vida_max,
            ataque=detalles.jugador_ataque, defensa=detalles.jugador_defensa,
            velocidad=detalles.jugador_velocidad, sala=detalles.sala_inicial,
            tiempo_siguiente=0, inventario_max=detalles.inventario_max,
        )
        # 2.4: la primera acción del jugador está programada en t=0.
        evento_inicial = simulacion.agenda.insertar(0, jugador, "accion_actor")
        jugador._proximo_evento = evento_inicial

        return [jugador, simulacion]

    def sincronizar_jugador(self, jugador, simulacion):
        estado = self._gestor.estado
        estado.reloj_virtual = simulacion.reloj.tiempo_actual
        estado.jugador_vida = jugador.vida
        estado.jugador_ataque = jugador.ataque
        estado.jugador_defensa = jugador.defensa
        estado.jugador_velocidad = jugador.velocidad

    def iniciar(self, detalles, nombre: str, semilla: int, modo: str):
        self.reiniciar()
        self._gestor.estado = EstadoPartida(
            activa=True,
            nombre_jugador=nombre,
            cripta_id=detalles.id,
            version_cripta=detalles.version,
            semilla=semilla,
            modo=modo,
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


    def comprobar_derrota(self, vivo: bool, resumen_red: str):
        if not vivo:
            self._gestor.estado.derrota = True
            self._gestor.estado.terminada = True
            self._gestor.estado.activa = False
            self._bitacora.append(Mensaje("sistema", "Has muerto."))
            self._bitacora.append(Mensaje("sistema", resumen_red))

    def registrar_apertura_salida(self, sala, salida):
        estado = self._gestor.estado
        if salida.sala_destino == estado.sala_salida_id and salida.llave == estado.llave_salida:
            puerta = [sala, salida.direccion]
            if puerta not in self._salidas_abiertas:
                self._gestor.historial.cambiar(self, "_salidas_abiertas", self._salidas_abiertas + [puerta])

    def comprobar_victoria(self, sala_origen, direccion, resumen_red):
        estado = self._gestor.estado
        if (estado.activa and estado.sala_actual_id == estado.sala_salida_id
                and [sala_origen, direccion] in self._salidas_abiertas):
            estado.victoria = True
            estado.terminada = True
            estado.activa = False
            self._bitacora.append(Mensaje("sistema", "Has escapado de la cripta. ¡Victoria!"))
            self._bitacora.append(Mensaje("sistema", resumen_red))

    def iniciar_registro(self, detalles, version_catalogo, semilla, nombre, capacidad_cache):
        if self._registro is not None:
            self._registro.iniciar(Cabecera(
                detalles.id, detalles.version, version_catalogo, semilla, nombre, capacidad_cache,
            ))
            self._bitacora.append(Mensaje("sistema", f"Registro: {self._registro.ruta}"))

    def puntajes(self):
        return self._puntajes.ordenados() if self._puntajes is not None else []

    def registrar_accion(self, nombre, argumento=None):
        if self._registro is not None:
            try:
                self._registro.anexar(nombre, argumento)
            except OSError as error:
                # Un fallo de disco detiene la sesion para no seguir sin registro.
                self._gestor.estado.activa = False
                raise ErrorRegistro(f"No se pudo registrar la accion: {error}") from error

    def retroceder(self) -> ResultadoAccion:
        if not self._gestor.estado.activa:
            return ResultadoAccion.fallo("La partida no está activa.")
        inv = self._gestor.inventario
        pergamino = next((item for item in inv.items()
                          if item.clase == "pergamino_retroceso"), None)
        if pergamino is None:
            return ResultadoAccion.fallo("No tienes pergaminos.")
        if not len(self._gestor.historial):
            return ResultadoAccion.fallo("No hay nada que deshacer.")
        self.registrar_accion("retroceder")
        inv.soltar_por_id(pergamino.instancia_id)
        self._gestor.deshacer()
        return ResultadoAccion.exito()

    def guardar_puntaje(self):
        if self.trucos_activos or self._puntajes is None or self._puntaje_guardado or self._partida_id is None:
            return
        estado = self._gestor.estado
        resultado = "victoria" if estado.victoria else "derrota" if estado.derrota else "abandono"
        try:
            self._puntajes.registrar(Puntaje(
                self._partida_id, estado.nombre_jugador, estado.cripta_id, estado.version_cripta,
                estado.acciones_ejecutadas, estado.enemigos_derrotados, estado.reloj_virtual, resultado))
        except (OSError, ValueError) as error:
            self.error_puntaje = f"No se pudo guardar el puntaje: {error}"
            self._bitacora.append(Mensaje("sistema", self.error_puntaje))
            return
        self._puntaje_guardado = True
        self.error_puntaje = ""

    def terminar(self, resumen_red: str) -> None:
        if self._gestor.estado.terminada:
            self.guardar_puntaje()
            return
        if self._registro is not None and self._registro.ruta is not None:
            self.registrar_accion("terminar")
        self._gestor.estado.activa = False
        self._gestor.estado.terminada = True
        self.guardar_puntaje()
        self._bitacora.append(Mensaje("sistema", resumen_red))
