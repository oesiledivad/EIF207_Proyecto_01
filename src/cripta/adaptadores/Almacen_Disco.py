"""Almacenamiento persistente en disco para la caché (§4.4).

Guarda las respuestas crudas (JSON) del servicio para no volver a pedirlas
por red mientras su versión siga vigente:

    <carpeta>/
        criptas.json                   lista de criptas (para jugar con --offline)
        detalles/<id>.json             datos generales de cada cripta descargada
        catalogo/version.txt           versión global del catálogo
        catalogo/fichas/<id>.json      una ficha por archivo
        criptas/<id>/version.txt       versión de la cripta
        criptas/<id>/salas_<n>.json    página n del esqueleto
        criptas/<id>/contenido/<sala>.json

Un archivo por ficha: recuperar una ficha liberada de memoria cuesta una
sola lectura de disco (abrir ese archivo), sin leer las demás. El sistema de
archivos hace de índice; no se usa dict como caché (§7).

Es un adaptador (§6): el modelo no sabe que existe.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def _nombre_seguro(texto: str) -> str:
    """Convierte un id en un nombre de archivo válido en cualquier sistema operativo."""
    resultado = []
    for ch in str(texto):
        resultado.append(ch if ch.isalnum() or ch in "-_" else "_")
    return "".join(resultado)


class AlmacenDisco:
    def __init__(self, carpeta: str | Path) -> None:
        self._raiz = Path(carpeta)
        self._dir_catalogo = self._raiz / "catalogo"
        self._dir_fichas = self._dir_catalogo / "fichas"
        self._dir_criptas = self._raiz / "criptas"
        self._dir_fichas.mkdir(parents=True, exist_ok=True)
        self._dir_criptas.mkdir(parents=True, exist_ok=True)

    #  Lectura / escritura básicas

    @staticmethod
    def _leer_json(ruta: Path) -> dict | None:
        if not ruta.exists():
            return None
        try:
            with ruta.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None  # archivo dañado: se trata como si no estuviera

    @staticmethod
    def _escribir_json(ruta: Path, datos: dict) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = ruta.with_suffix(".tmp")
        with temporal.open("w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False)
        temporal.replace(ruta)  # escritura atómica: nunca queda un archivo a medias

    @staticmethod
    def _leer_texto(ruta: Path) -> str | None:
        if not ruta.exists():
            return None
        return ruta.read_text(encoding="utf-8").strip()

    #  Validación por versión

    def validar_catalogo(self, version: str) -> bool:
        """Si la versión del catálogo cambió, borra todas las fichas guardadas.

        Returns:
            True si lo persistido seguía vigente; False si se invalidó.
        """
        ruta = self._dir_catalogo / "version.txt"
        vigente = self._leer_texto(ruta) == version
        if not vigente:
            shutil.rmtree(self._dir_fichas, ignore_errors=True)
            self._dir_fichas.mkdir(parents=True, exist_ok=True)
            ruta.write_text(version, encoding="utf-8")
        return vigente

    def validar_cripta(self, cripta_id: str, version: str) -> bool:
        """Si la versión de la cripta cambió, borra su esqueleto y contenido guardados."""
        carpeta = self._dir_criptas / _nombre_seguro(cripta_id)
        ruta = carpeta / "version.txt"
        vigente = self._leer_texto(ruta) == version
        if not vigente:
            shutil.rmtree(carpeta, ignore_errors=True)
            carpeta.mkdir(parents=True, exist_ok=True)
            ruta.write_text(version, encoding="utf-8")
        return vigente

    #  Fichas de catálogo

    def leer_ficha(self, id_ficha: str) -> dict | None:
        return self._leer_json(self._dir_fichas / f"{_nombre_seguro(id_ficha)}.json")

    def guardar_ficha(self, bruto: dict) -> None:
        self._escribir_json(self._dir_fichas / f"{_nombre_seguro(bruto['id'])}.json", bruto)

    #  Esqueleto y contenido

    def _dir_cripta(self, cripta_id: str) -> Path:
        return self._dir_criptas / _nombre_seguro(cripta_id)

    def leer_pagina_salas(self, cripta_id: str, pagina: int) -> dict | None:
        return self._leer_json(self._dir_cripta(cripta_id) / f"salas_{pagina}.json")

    def guardar_pagina_salas(self, cripta_id: str, pagina: int, datos: dict) -> None:
        self._escribir_json(self._dir_cripta(cripta_id) / f"salas_{pagina}.json", datos)

    def leer_contenido(self, cripta_id: str, sala_id: int) -> dict | None:
        return self._leer_json(self._dir_cripta(cripta_id) / "contenido" / f"{int(sala_id)}.json")

    def guardar_contenido(self, cripta_id: str, entrada: dict) -> None:
        sala_id = int(entrada.get("sala", 0))
        self._escribir_json(self._dir_cripta(cripta_id) / "contenido" / f"{sala_id}.json", entrada)

    #  Datos generales (los usa --offline para jugar lo ya descargado)

    def guardar_lista_criptas(self, datos: dict) -> None:
        self._escribir_json(self._raiz / "criptas.json", datos)

    def leer_lista_criptas(self) -> dict | None:
        return self._leer_json(self._raiz / "criptas.json")

    def guardar_detalles(self, cripta_id: str, datos: dict) -> None:
        # Fuera de criptas/<id>/: validar_cripta borra esa carpeta si cambia la versión.
        self._escribir_json(self._raiz / "detalles" / f"{_nombre_seguro(cripta_id)}.json", datos)

    def leer_detalles(self, cripta_id: str) -> dict | None:
        return self._leer_json(self._raiz / "detalles" / f"{_nombre_seguro(cripta_id)}.json")

    def leer_version_catalogo(self) -> str | None:
        return self._leer_texto(self._dir_catalogo / "version.txt")
