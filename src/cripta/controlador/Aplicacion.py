"""Controlador de Aplicación (MVC).
"""

from __future__ import annotations

from pathlib import Path
from cripta.controlador.ExploracionControlador import ExploracionControlador
from cripta.controlador.GuardadoControlador import GuardadoControlador
from cripta.controlador.CheatsControlador import CheatsControlador
from cripta.controlador.InicioPartidaControlador import InicioPartidaControlador
from cripta.controlador.CicloAccionesControlador import CicloAccionesControlador

from cripta.adaptadores.Crypt_Data_Source import CryptDataSource
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.controlador.GestorPartida import GestorPartida
from cripta.controlador.PartidaControlador import PartidaControlador
from cripta.controlador.InventarioControlador import InventarioControlador
from cripta.controlador.CombateControlador import CombateControlador
from cripta.controlador.EfectosControlador import EfectosControlador

from cripta.dto.Partida_dto import (
    CriptaResumen,
    DetallesCripta,
    EstadoPartida,
    ResultadoInicio,
    SalaModelo,
)
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.servicio.CriptaService import CriptaService
from cripta.modelo.Simulacion import Simulacion
from cripta.modelo.Jugador import Jugador

from cripta.estructuras.Indice_Salas import IndiceSalas

class Aplicacion:
    """Controlador de Aplicación.

    Args:
        data_source: Adaptador de datos (red u offline).
        capacidad_cache: Tope de fichas en memoria (--cache-size, 4.4).
        almacen: Caché persistente en disco (None = desactivada).
    """

    def __init__(self, data_source: CryptDataSource, capacidad_cache: int = 25,
                almacen: AlmacenDisco | None = None, carpeta_logs=None, ruta_puntajes=None, ruta_guardado=None,
                offline_dir=None) -> None:
        self._cripta_service = CriptaService(
            data_source, Cache_Fichas(capacidad=capacidad_cache), almacen
        )
        self._gestor = GestorPartida()
        self._bitacora = Bitacora(capacidad=20)
        self._inventario = InventarioControlador(self._gestor, self._bitacora, self._cripta_service)
        self._efectos = EfectosControlador(self._gestor, self._bitacora, self._cripta_service)
        self._combate = CombateControlador(self._gestor, self._bitacora, self._cripta_service, self._efectos)
        self._simulacion: Simulacion | None = None
        self._jugador: Jugador | None = None
        self._exploracion = ExploracionControlador(self)  # Cambio(kyara)

        self._partida = PartidaControlador(self._gestor, self._bitacora, carpeta_logs, ruta_puntajes)
        self._guardado = GuardadoControlador(self, capacidad_cache, almacen, carpeta_logs, ruta_puntajes,
                                             ruta_guardado, offline_dir if offline_dir is not None
                                             else getattr(data_source, "carpeta", "datos_prueba"))
        self._cheats = CheatsControlador(self)
        self._inicio = InicioPartidaControlador(self)
        self._ciclo = CicloAccionesControlador(self)

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
        registrar: bool = True,
    ) -> ResultadoInicio:
        return self._inicio.iniciar(nombre_jugador, semilla, cripta_id, registrar)

    #  Salas y exploración (delegado a ExploracionControlador)
    @property
    def _salas(self) -> IndiceSalas:
        return self._exploracion.salas

    @_salas.setter
    def _salas(self, valor: IndiceSalas) -> None:
        self._exploracion.salas = valor

    def _crear_salas_desde_esqueleto(self, esqueleto: list[SalaModelo]) -> None:
        self._exploracion.ensamblar_salas(esqueleto)

    def _cargar_lote(self, origen_id: int) -> None:
        self._exploracion.cargar_lote(origen_id)

    def _avisar(self, mensaje: str | None) -> None:
        if mensaje is not None:
            self._bitacora.append(Mensaje("sistema", mensaje))

    def _tipos_activos(self) -> list[str]:
        return self._cripta_service.tipos_activos(
            self._gestor.inventario, self._salas, self._salas.obtener(self._jugador.sala))

    #  Ciclo de una acción del jugador (2.3)

    def _partida_en_curso(self) -> bool:
        return (self._simulacion is not None and self._jugador is not None
                and self._gestor.estado.activa)

    def _accion_jugador(self, nombre_costo: str, ejecutar, argumento=None) -> ResultadoAccion:
        # Punto fijo para incorporar la precarga en segundo plano (determinista, 4.2).
        self._avisar(self._cripta_service.completar_precarga())
        return self._ciclo.ejecutar(nombre_costo, ejecutar, argumento)

    def activar_precarga_en_segundo_plano(self) -> None:
        """Solo la vista interactiva: replay, bench y pruebas quedan sincrónicos."""
        self._cripta_service.activar_precarga_en_segundo_plano()

    def _despues_del_ciclo(self) -> None:
        self._ciclo.finalizar()

    def _actualizar_vecindad(self) -> None:
        self._exploracion.actualizar_vecindad()

    def _sincronizar_estado(self) -> None:
        self._ciclo.sincronizar()

    # ---- acción: esperar ----

    def esperar(self) -> ResultadoAccion:
        return self._accion_jugador("esperar", self._ejecutar_espera)

    def _ejecutar_espera(self) -> ResultadoAccion:
        self._bitacora.append(Mensaje("jugador", "Esperás."))
        return ResultadoAccion.exito()

    #  Consultas de juego

    def estado_partida(self) -> EstadoPartida:
        return self._gestor.estado

    def bitacora(self) -> Bitacora:
        return self._bitacora

    def solicitudes_usadas(self) -> int:
        return self._cripta_service.requests_made

    @property
    def presupuesto_agotado(self) -> bool:
        """Indica si la sesión ya no puede realizar solicitudes HTTP."""
        return self._cripta_service.solicitudes_restantes() == 0

    def resumen_red(self) -> str:
        """5.1: solicitudes realizadas, presupuesto, aciertos y fallos de caché."""
        s = self._cripta_service
        return (f"Red: {s.requests_made}/{self._gestor.estado.presupuesto_solicitudes} solicitudes · "
                f"caché: {s.aciertos_cache} aciertos, {s.fallos_cache} fallos, "
                f"{s.lecturas_disco} lecturas de disco")

    #  Guardados y ayudas de pruebas (delegados)
    @property
    def ruta_guardado(self):
        """Expone la ruta configurada sin administrar los archivos."""
        return self._guardado.ruta

    @ruta_guardado.setter
    def ruta_guardado(self, ruta):
        """Actualiza la ruta configurada mediante el controlador de guardado."""
        self._guardado.ruta = Path(ruta)

    def guardar(self, ruta=None) -> ResultadoAccion:
        """Delega el guardado sin consumir tiempo virtual."""
        return self._guardado.guardar(ruta)

    def listar_guardados(self):
        """Devuelve los guardados identificados por jugador y progreso."""
        return self._guardado.listar()

    def cargar(self, ruta=None) -> ResultadoAccion:
        """Delega la carga con la fuente actual."""
        return self._guardado.cargar(ruta)

    def cargar_compatible(self, ruta=None):
        """Delega la carga con selección de fuente según el guardado."""
        return self._guardado.cargar_compatible(ruta)

    @property
    def trucos_activos(self):
        """Indica si la sesión está marcada como prueba."""
        return self._partida.trucos_activos

    def truco_activo(self, nombre):
        """Consulta un interruptor de cheats."""
        return self._cheats.activo(nombre)

    def aplicar_truco(self, nombre):
        """Delega una ayuda sin consumir tiempo virtual."""
        return self._cheats.aplicar(nombre)

    #  Inventario (delegado a InventarioController; aquí se les da costo de tiempo)

    def recoger(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador("recoger", lambda: self._inventario.recoger(instancia_id), instancia_id)

    def soltar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador("soltar", lambda: self._inventario.soltar(instancia_id, self._jugador), instancia_id)

    def equipar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador("equipar_objeto", lambda: self._inventario.equipar(instancia_id, self._jugador), instancia_id)

    def usar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador(
            "usar_objeto",
            lambda: self._inventario.usar(instancia_id, self._jugador, self._simulacion,
                                          self._efectos),
            instancia_id,
        )

    def usar_pergamino(self) -> ResultadoAccion:
        if not self._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")
        anteriores = self._tipos_activos()
        resultado = self._partida.retroceder()
        if resultado.ok:
            self._avisar(self._cripta_service.reproteger(anteriores, self._tipos_activos()))
            self._despues_del_ciclo()
            self._bitacora.append(Mensaje("efecto", "Usaste un pergamino de retroceso."))
        return resultado

    def siguiente_item(self) -> ResultadoAccion:
        return self._recorrer_inventario(self._inventario.siguiente, "siguiente_item")

    def anterior_item(self) -> ResultadoAccion:
        return self._recorrer_inventario(self._inventario.anterior, "anterior_item")

    def seleccionar_item(self, instancia_id: str) -> ResultadoAccion:
        """Registra una selección directa sin consumir tiempo virtual."""
        return self._recorrer_inventario(lambda: self._inventario.seleccionar(instancia_id),
                                        "seleccionar_item", instancia_id)

    def _recorrer_inventario(self, recorrer, nombre: str, argumento=None) -> ResultadoAccion:
        if not self._partida_en_curso():
            return ResultadoAccion.fallo("La partida no está activa.")
        return self._inventario.recorrer(recorrer, nombre, self._partida.registrar_accion, argumento)

    def inventario(self):
        """Devuelve el inventario activo o None."""
        return self._gestor.inventario

    #  Acciones de partida

    def mover(self, direccion: str) -> ResultadoAccion:
        return self._exploracion.mover(direccion)

    def abrir(self, direccion: str) -> ResultadoAccion:
        """Abre la puerta de la sala actual en `direccion` (2.5). Costo 50."""
        return self._exploracion.abrir(direccion)

    abrir_puerta = abrir

    def atacar(self, instancia_id: str) -> ResultadoAccion:
        return self._accion_jugador(
            "atacar",
            lambda: self._combate.atacar(instancia_id, self._jugador, self._simulacion, self._salas),
            instancia_id,
        )

    def puntajes(self):
        return self._partida.puntajes()

    @property
    def error_puntaje(self):
        return self._partida.error_puntaje

    def terminar(self) -> None:
        self._cripta_service.esperar_precarga()   # sus solicitudes entran en el resumen
        self._partida.terminar(self.resumen_red())

    def preparar_seleccion(self):
        """Prepara una nueva sesión antes de mostrar la selección de criptas."""
        self._inicio.preparar_seleccion()
