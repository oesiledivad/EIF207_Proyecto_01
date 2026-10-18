"""Registro JSON por linea, solo anexado; replay sin interfaz."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Cabecera:
    cripta_id: str
    version_cripta: str
    version_catalogo: str
    semilla: int
    nombre_jugador: str
    capacidad_cache: int
    formato: int = 1


def _validar_accion(nombre, argumento):
    if nombre in ["esperar", "retroceder", "siguiente_item", "anterior_item", "terminar"]:
        if argumento is not None:
            raise ValueError("La accion no admite argumento.")
    elif nombre in ["mover", "recoger", "soltar", "equipar_objeto", "usar_objeto", "atacar", "abrir_puerta",
                    "seleccionar_item"]:
        if not isinstance(argumento, str) or not argumento.strip():
            raise ValueError("La accion requiere un argumento de texto.")
        if nombre in ["mover", "abrir_puerta"] and argumento not in ["N", "S", "E", "O"]:
            raise ValueError("Direccion invalida.")
    else:
        raise ValueError(f"Accion desconocida: {nombre!r}.")


class ErrorRegistro(RuntimeError):
    """No se pudo persistir una accion; la sesion debe detenerse."""


class RegistroPartida:
    def __init__(self, carpeta):
        self.carpeta = Path(carpeta)
        self.ruta = None

    def _siguiente_ruta(self, cripta_id):
        prefijo = "".join(ch if ch.isalnum() else "_" for ch in cripta_id).strip("_") or "cripta"
        numeros = [ruta.stem.rsplit("_", 1)[-1]
                   for ruta in self.carpeta.glob(f"{prefijo}_partida_*.log")]
        numero = 1 + max((int(n) for n in numeros if n.isdecimal()), default=0)
        return self.carpeta / f"{prefijo}_partida_{numero:05d}.log"

    def iniciar(self, cabecera: Cabecera):
        self.carpeta.mkdir(parents=True, exist_ok=True)
        while True:
            ruta = self._siguiente_ruta(cabecera.cripta_id)
            try:
                # Creacion exclusiva: tampoco sobrescribe si coinciden dos procesos.
                with ruta.open("x", encoding="utf-8") as archivo:
                    archivo.write(json.dumps(asdict(cabecera), ensure_ascii=False) + "\n")
            except FileExistsError:
                continue
            self.ruta = ruta
            break

    def anexar(self, nombre, argumento=None):
        _validar_accion(nombre, argumento)
        if self.ruta is None:
            raise RuntimeError("El registro no tiene encabezado.")
        with self.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps([nombre, argumento], ensure_ascii=False) + "\n")


def leer_partida(ruta):
    with Path(ruta).open(encoding="utf-8") as archivo:
        try:
            cabecera = Cabecera(**json.loads(archivo.readline()))
        except (ValueError, TypeError) as error:
            raise ValueError("Encabezado de replay invalido.") from error
        if (type(cabecera.formato) is not int or cabecera.formato != 1
                or type(cabecera.semilla) is not int or cabecera.semilla < 0
                or type(cabecera.capacidad_cache) is not int or cabecera.capacidad_cache <= 0
                or any(not isinstance(valor, str) or not valor.strip() for valor in
                       [cabecera.cripta_id, cabecera.version_cripta,
                        cabecera.version_catalogo, cabecera.nombre_jugador])):
            raise ValueError("Encabezado de replay incompatible o incompleto.")
        acciones = []
        for linea, texto in enumerate(archivo, 2):
            try:
                accion = json.loads(texto)
                if not isinstance(accion, list) or len(accion) != 2:
                    raise ValueError("Se esperaba [accion, argumento].")
                _validar_accion(*accion)
            except (ValueError, TypeError) as error:
                raise ValueError(f"Replay invalido en linea {linea}: {error}") from error
            acciones.append(accion)
    return [cabecera, acciones]


def reproducir(ruta, fuentes):
    from cripta.controlador.Aplicacion import Aplicacion

    cabecera, acciones = leer_partida(ruta)
    app = None
    errores = []
    for fuente in fuentes:
        candidato = Aplicacion(fuente, capacidad_cache=cabecera.capacidad_cache)
        try:
            detalles = candidato.previsualizar_cripta(cabecera.cripta_id)
            candidato._cripta_service.fijar_presupuesto(detalles.presupuesto_solicitudes)
            version_catalogo = candidato._cripta_service.obtener_version_catalogo()
            if (detalles.version != cabecera.version_cripta
                    or version_catalogo != cabecera.version_catalogo):
                raise ValueError("Version de cripta o catalogo incompatible.")
            resultado = candidato.iniciar_partida(
                cabecera.nombre_jugador, str(cabecera.semilla), cabecera.cripta_id)
            if not resultado.ok:
                raise ValueError(f"No se pudo iniciar el replay: {resultado.motivo}")
        except (OSError, RuntimeError, ValueError, NotImplementedError) as error:
            errores.append(str(error))
            continue
        app = candidato
        break
    if app is None:
        raise ValueError("No se puede garantizar una reproduccion fiel: " + "; ".join(errores))
    for linea, (nombre, argumento) in enumerate(acciones, 2):
        match nombre:
            case "retroceder":
                resultado = app.usar_pergamino()
            case "equipar_objeto":
                resultado = app.equipar(argumento)
            case "usar_objeto":
                resultado = app.usar(argumento)
            case "terminar":
                app.terminar()
                continue
            case "esperar" | "siguiente_item" | "anterior_item":
                resultado = getattr(app, nombre)()
            case _:
                resultado = getattr(app, nombre)(argumento)
        if not resultado.ok:
            raise ValueError(f"Replay divergente en linea {linea}: {resultado.motivo}")
    return app
