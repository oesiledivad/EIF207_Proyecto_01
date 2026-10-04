"""Arranque de la aplicación.

Lee flags, elige adaptador (red u offline), construye el controlador
y lanza la vista Textual. No es controlador MVC: solo prepara el arranque.

Solo se soporta --offline. --replay, --bench y --cache-size
se añadirán cuando existan sus módulos.
"""

from __future__ import annotations

import argparse
import sys

from cripta.adaptadores.Crypt_Data_Source import CryptDataSource
from cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.controlador.Aplicacion import Aplicacion


def _parsear_args(argv: list[str]) -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos.

    Args:
        argv: Lista de argumentos pasados al programa.

    Returns:
        Los argumentos parseados como un objeto Namespace.
    """
    parser = argparse.ArgumentParser(
        prog="cripta",
        description="Cripta · juego de mazmorra dirigido por eventos.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Usa el paquete de respuestas descargadas en lugar de la red.",
    )
    return parser.parse_args(argv)


def _construir_data_source(args: argparse.Namespace) -> CryptDataSource:
    """Construye y retorna el adaptador de datos correspondiente a los argumentos.

    Args:
        args: Argumentos de línea de comandos parseados.

    Returns:
        Instancia de CryptDataSource (OfflineAdapter o NetworkAdapter).
    """
    if args.offline:
        return AdaptadorOffline("datos_prueba")
    return NetworkAdapter()


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal de la aplicación.

    Args:
        argv: Lista opcional de argumentos. Si es None, utiliza sys.argv[1:].

    Returns:
        Código de salida de la aplicación (0 para éxito).
    """
    args = _parsear_args(argv if argv is not None else sys.argv[1:])

    data_source = _construir_data_source(args)
    controlador = Aplicacion(data_source)

    # Import diferido: la vista Textual solo se construye si vamos a usarla.
    from cripta.vista.textual.app import CriptaApp

    app = CriptaApp(controlador)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())