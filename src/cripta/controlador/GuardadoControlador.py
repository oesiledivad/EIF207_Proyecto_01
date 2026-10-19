"""Coordinación del guardado; reutiliza el formato y la restauración"""
import struct
from datetime import datetime
from pathlib import Path

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.controlador.guardado import escribir_partida, leer_partida, restaurar_partida
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Mensaje
from cripta.estructuras.Ordenamientos import ordenar


class GuardadoControlador:
    """Administra archivos por partida y selecciona la fuente de datos al cargar."""

    def __init__(self, aplicacion, capacidad_cache, almacen, carpeta_logs, ruta_puntajes,
                 ruta_guardado, offline_dir):
        """Conserva rutas y opciones necesarias para reconstruir otra sesión.

        Args:
            aplicacion: Contexto de la sesión actual.
            capacidad_cache: Tope de fichas de una sesión reconstruida.
            almacen: Caché persistente para partidas de red.
            carpeta_logs: Carpeta de registros y guardados.
            ruta_puntajes: Archivo configurado para la tabla de puntajes.
            ruta_guardado: Ruta fija opcional, también compatible con guardados antiguos.
            offline_dir: Carpeta de las respuestas offline.
        """
        self._app = aplicacion
        self.capacidad_cache = capacidad_cache
        self.almacen = almacen
        self.carpeta_logs = carpeta_logs
        self.ruta_puntajes = ruta_puntajes
        self.offline_dir = offline_dir
        self.ruta = Path(ruta_guardado) if ruta_guardado is not None else Path("partida_guardada.bin")
        self.ruta_fija = ruta_guardado is not None
        self.actual = None
        self.carpeta = Path(carpeta_logs or "partidas") / "guardadas"

    def ruta_para_guardar(self):
        """Devuelve un archivo por partida, identificado por cripta y jugador."""
        estado = self._app.estado_partida()
        partes = ["".join(c if c.isalnum() or c in "_-" else "_" for c in texto)[:40]
                  for texto in [estado.cripta_id, estado.nombre_jugador]]
        return self.carpeta / f"{partes[0]}_{partes[1]}_{self._app._partida.identificador}.bin"

    def listar(self):
        """Devuelve pares [ruta, descripción], incluyendo archivos ilegibles."""
        rutas = list(self.carpeta.glob("*.bin"))
        if self.ruta.is_file() and self.ruta.resolve() not in [ruta.resolve() for ruta in rutas]:
            rutas.append(self.ruta)
        guardados = []
        for ruta in ordenar(rutas, key=lambda archivo: archivo.name):
            try:
                datos = leer_partida(ruta)
                fecha = datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%d/%m %H:%M")
                descripcion = (f"{datos.nombre_jugador} · {datos.cripta_id} · sala {datos.sala_actual_id}"
                               f" · {datos.modo} · t={datos.tiempo_actual} · {fecha}")
            except (OSError, ValueError, struct.error):
                descripcion = f"Guardado ilegible: {ruta.name}"
            guardados.append([ruta, descripcion])
        return guardados

    def guardar(self, ruta=None):
        """Guarda la sesión activa sin consumir tiempo; rechaza sesiones con cheats."""
        app = self._app
        if not app._partida_en_curso():
            return ResultadoAccion.fallo("No hay una partida activa para guardar.")
        if app.trucos_activos:
            return ResultadoAccion.fallo("Las partidas con cheats no se guardan.")
        destino = Path(ruta) if ruta is not None else self.actual
        if destino is None:
            destino = self.ruta if self.ruta_fija else self.ruta_para_guardar()
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            escribir_partida(app, destino)
        except (OSError, ValueError) as error:
            return ResultadoAccion.fallo(f"No se pudo guardar: {error}")
        self.actual = destino
        app._bitacora.append(Mensaje("sistema", f"Partida guardada en {destino}."))
        return ResultadoAccion.exito()

    def cargar(self, ruta=None):
        """Valida y restaura un guardado compatible con la fuente actual."""
        app = self._app
        origen = Path(ruta) if ruta is not None else (self.actual or self.ruta)
        try:
            datos = leer_partida(origen)
        except (OSError, ValueError, struct.error) as error:
            return ResultadoAccion.fallo(f"No se pudo leer el guardado: {error}")
        modo = "offline" if app._cripta_service.es_offline() else "red"
        if datos.modo != modo:
            return ResultadoAccion.fallo(f"El guardado es de modo {datos.modo}; debe cargarse con esa fuente de datos.")
        try:
            detalles = app._cripta_service.obtener_detalles(datos.cripta_id)
        except (PresupuestoAgotado, RuntimeError) as error:
            return ResultadoAccion.fallo(f"No se pudo validar la cripta del guardado: {error}")
        if detalles.version != datos.version_cripta:
            return ResultadoAccion.fallo("La cripta cambió de versión desde que se guardó.")
        # Una carga no empieza en t=0: el replay se reanuda al iniciar otra partida.
        resultado = app.iniciar_partida(datos.nombre_jugador, str(datos.semilla), datos.cripta_id, registrar=False)
        if not resultado.ok:
            return ResultadoAccion.fallo(resultado.motivo)
        try:
            restaurar_partida(app, datos)
        except (ValueError, KeyError, RuntimeError) as error:
            app._gestor.estado.activa = False
            return ResultadoAccion.fallo(f"El guardado no coincide con la cripta: {error}")
        self.actual = origen
        app._bitacora.append(Mensaje("sistema", f"Partida cargada de {origen}."))
        return ResultadoAccion.exito()

    def cargar_compatible(self, ruta=None):
        """Devuelve [resultado, aplicación] y cambia de fuente solo si la carga funciona."""
        app = self._app
        origen = Path(ruta) if ruta is not None else (self.actual or self.ruta)
        try:
            datos = leer_partida(origen)
            if datos.modo not in ["red", "offline"]:
                return [ResultadoAccion.fallo("Modo de guardado desconocido."), app]
            modo = "offline" if app._cripta_service.es_offline() else "red"
            if datos.modo == modo:
                return [self.cargar(origen), app]
            fuente = (AdaptadorOffline(self.offline_dir, almacen=self.almacen) if datos.modo == "offline"
                      else NetworkAdapter())
            nuevo = type(app)(fuente, capacidad_cache=self.capacidad_cache,
                              almacen=self.almacen if datos.modo == "red" else None,
                              carpeta_logs=self.carpeta_logs, ruta_puntajes=self.ruta_puntajes,
                              ruta_guardado=self.ruta if self.ruta_fija else None,
                              offline_dir=self.offline_dir)
            if app._cripta_service.precarga_en_segundo_plano:
                nuevo.activar_precarga_en_segundo_plano()
            return [nuevo.cargar(origen), nuevo]
        except (OSError, RuntimeError, ValueError, struct.error) as error:
            return [ResultadoAccion.fallo(f"No se pudo cargar el guardado: {error}"), app]
