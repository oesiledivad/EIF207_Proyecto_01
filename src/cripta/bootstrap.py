"""Arranque de la aplicación.

Lee flags, elige adaptador (red u offline), construye el controlador
y lanza la vista gráfica (Arcade). No es controlador MVC: solo prepara el arranque.

El modo --bench ejecuta mediciones sin red ni vista interactiva.
"""

from __future__ import annotations

import argparse
import sys

from cripta.adaptadores.Crypt_Data_Source import CryptDataSource
from cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
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
        help="Juega sin red con lo ya descargado en --cache-dir; el paquete --offline-dir "
             "solo completa lo que la caché no tenga.",
    )
    parser.add_argument(
        "--cache-size",
        type=int,
        default=25,
        help="Tope de fichas de catálogo en memoria (4.4). Por defecto 25.",
    )
    parser.add_argument(
        "--cache-dir",
        default=".cripta_cache",
        help="Carpeta de la caché persistente (fichas, esqueleto, contenido).",
    )
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument("--replay", metavar="PARTIDA.LOG",
                       help="Reproduce acciones sin interfaz; exige versiones compatibles.")
    parser.add_argument("--puntajes", help="Archivo de puntajes (por defecto, dentro de --log-dir).")
    parser.add_argument("--log-dir", default="partidas", help="Carpeta de registros de partida.")
    parser.add_argument("--offline-dir", default="datos_prueba", help="Paquete de respuestas del curso (respaldo de --offline).")
    modos.add_argument("--bench", action="store_true",
                        help="Ejecuta cargas sinteticas sin red ni interfaz.")
    modos.add_argument("--grafica", action="store_true",
                       help="Vista Arcade (ya es la predeterminada; se acepta por compatibilidad).")
    parser.add_argument("--cripta", help="Id de cripta preseleccionada en el menú.")
    parser.add_argument("--nombre", default="Jugador", help="Nombre inicial del jugador.")
    parser.add_argument("--semilla", default="", help="Semilla inicial (vacía = aleatoria).")
    return parser.parse_args(argv)


def _construir_data_source(args: argparse.Namespace) -> CryptDataSource:
    """Construye y retorna el adaptador de datos correspondiente a los argumentos.

    Args:
        args: Argumentos de línea de comandos parseados.

    Returns:
        Instancia de CryptDataSource (OfflineAdapter o NetworkAdapter).
    """
    if args.offline:
        # Primero lo descargado al jugar en línea (--cache-dir); el paquete del
        # curso (--offline-dir) solo completa lo que la caché no tenga.
        return AdaptadorOffline(args.offline_dir, almacen=AlmacenDisco(args.cache_dir))
    return NetworkAdapter()


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal de la aplicación.

    Args:
        argv: Lista opcional de argumentos. Si es None, utiliza sys.argv[1:].

    Returns:
        Código de salida de la aplicación (0 para éxito).
    """
    args = _parsear_args(argv if argv is not None else sys.argv[1:])

    if args.cache_size <= 0:
        print("--cache-size debe ser un entero positivo.", file=sys.stderr)
        return 2
    if args.bench:
        from cripta.bench import main as medir
        medir()
        return 0

    data_source = _construir_data_source(args)
    if args.replay:
        from cripta.replay.reproductor import reproducir
        # El paquete se valida por separado: una caché incompleta no lo oculta.
        fuentes = [data_source, AdaptadorOffline(args.offline_dir)]
        try:
            controlador = reproducir(args.replay, fuentes, mostrar_progreso=True)
        except (OSError, RuntimeError, ValueError) as error:
            print(str(error), file=sys.stderr)
            return 2
        estado = controlador.estado_partida()
        print(f"Replay completado: sala={estado.sala_actual_id} "
              f"vida={estado.jugador_vida} tiempo={estado.reloj_virtual}")
        print(controlador.resumen_red())
        return 0

    # En --offline los datos ya vienen de disco (la caché la lee el propio adaptador).
    almacen = None if args.offline else AlmacenDisco(args.cache_dir)
    controlador = Aplicacion(data_source, capacidad_cache=args.cache_size, almacen=almacen,
                             carpeta_logs=args.log_dir, ruta_puntajes=args.puntajes, offline_dir=args.offline_dir)
    # Ventana interactiva: la precarga va en un hilo para que cruzar puertas no se trabe.
    controlador.activar_precarga_en_segundo_plano()

    # Import diferido: arcade solo se carga si de verdad se abre la ventana.
    from cripta.vista.grafica import iniciar
    try:
        return iniciar(controlador, args.cripta, args.nombre, args.semilla, args.offline)
    except ModuleNotFoundError as error:
        if error.name != "arcade":
            raise
        print("Falta arcade. Instala las dependencias con: uv sync", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
