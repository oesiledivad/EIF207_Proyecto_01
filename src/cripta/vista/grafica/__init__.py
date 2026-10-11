"""Vista gráfica con Arcade; las animaciones no avanzan el reloj virtual.

arcade se importa solo al abrir la ventana: así los módulos puros (medidas,
fuente_pixel, distribucion) se pueden probar sin abrir ninguna ventana.
"""
import sys


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
    import arcade
    from .ventana import VentanaCripta
    from .menu import MenuPrincipal
    try:
        ventana = VentanaCripta(controlador, offline=offline)
        menu = MenuPrincipal(ventana, cripta_id, nombre, semilla)
        ventana.cargar("Buscando criptas", menu.cargar, lambda _: ventana.show_view(menu))
    except (OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    arcade.run()
    return 0


def __getattr__(nombre):
    """Importación diferida de VentanaCripta (requiere arcade)."""
    if nombre == "VentanaCripta":
        from .ventana import VentanaCripta
        return VentanaCripta
    raise AttributeError(nombre)
