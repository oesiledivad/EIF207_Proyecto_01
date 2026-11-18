"""Diagnóstico HTTP separado del registro reproducible de acciones."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


registro_red = logging.getLogger("cripta.red")
registro_red.addHandler(logging.NullHandler())
registro_red.propagate = False


def configurar_registro_red(carpeta):
    ruta = (Path(carpeta) / "red.log").resolve()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    for manejador in list(registro_red.handlers):
        if isinstance(manejador, RotatingFileHandler):
            registro_red.removeHandler(manejador)
            manejador.close()
    manejador = RotatingFileHandler(ruta, maxBytes=1_048_576, backupCount=3, encoding="utf-8")
    manejador.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    registro_red.addHandler(manejador)
    registro_red.setLevel(logging.INFO)
    return ruta
