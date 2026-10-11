"""Tabla local atomica; ordenamiento propio de los registros."""
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from cripta.estructuras.Ordenamientos import ordenar


@dataclass
class Puntaje:
    partida_id: str
    nombre_jugador: str
    cripta_id: str
    version_cripta: str
    acciones: int
    enemigos_derrotados: int
    tiempo_final: int
    resultado: str

    def __post_init__(self):
        if (any(not isinstance(valor, str) or not valor.strip() for valor in
                [self.partida_id, self.nombre_jugador, self.cripta_id, self.version_cripta])
                or any(type(valor) is not int or valor < 0 for valor in
                       [self.acciones, self.enemigos_derrotados, self.tiempo_final])
                or self.resultado not in ["victoria", "derrota", "abandono"]):
            raise ValueError("Registro de puntaje invalido.")


class TablaPuntajes:
    def __init__(self, ruta):
        self.ruta = Path(ruta)

    def leer(self):
        try:
            with self.ruta.open(encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            return []
        if not isinstance(datos, list):
            raise ValueError("Tabla de puntajes invalida; no se sobreescribira.")
        try:
            return [Puntaje(**registro) for registro in datos]
        except TypeError as error:
            raise ValueError("Tabla de puntajes invalida; no se sobreescribira.") from error

    def registrar(self, puntaje):
        registros = self.leer()
        if any(registro.partida_id == puntaje.partida_id for registro in registros):
            return
        registros.append(puntaje)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False,
                                             dir=self.ruta.parent, prefix=self.ruta.name + ".") as archivo:
                temporal = Path(archivo.name)
                json.dump([asdict(registro) for registro in registros], archivo, ensure_ascii=False)
                archivo.flush()
                os.fsync(archivo.fileno())
            os.replace(temporal, self.ruta)
        finally:
            if temporal is not None:
                temporal.unlink(missing_ok=True)

    def ordenados(self):
        return ordenar(self.leer(), key=lambda p: [
            p.resultado != "victoria", -p.enemigos_derrotados,
            p.acciones, p.tiempo_final, p.nombre_jugador, p.partida_id])
