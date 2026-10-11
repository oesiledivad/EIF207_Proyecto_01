"""Entrada del prototipo Arcade; las animaciones no avanzan el reloj virtual."""
import sys

import arcade

from .ventana import VentanaCripta
from .menu import MenuPrincipal


def iniciar(controlador, cripta_id, nombre, semilla, offline=True):
    """Abre el menú gráfico y ejecuta el ciclo de eventos de Arcade.

    Args:
        controlador: Aplicación que administra la partida.
        cripta_id: Cripta preseleccionada; None usa la primera disponible.
        nombre: Nombre inicial del jugador.
        semilla: Semilla escrita; vacía permite generar una.
        offline: Indica si los datos provienen de archivos locales.

    Returns:
        int: Código de salida; 2 si falla la preparación.
    """
    try:
        ventana = VentanaCripta(controlador, offline=offline)
        menu = MenuPrincipal(ventana, cripta_id, nombre, semilla)
        ventana.cargar("Buscando criptas", menu.cargar, lambda _: ventana.show_view(menu))
    except (OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    arcade.run()
    return 0
