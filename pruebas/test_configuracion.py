"""Ajustes de vista con clics reales, sin modificar la simulación."""
import unittest

from pruebas.test_grafica import COMUN, _ejecutar


class PruebasConfiguracion(unittest.TestCase):
    def test_menu_partida_volumen_limites_y_retorno(self):
        _ejecutar(self, COMUN + r'''
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.grafica.menu import MenuPrincipal
from cripta.vista.grafica.configuracion import Configuracion
from pruebas.test_replay import FuenteReplay, firma

app = Aplicacion(FuenteReplay())
vista = VentanaCripta(app, visible=False, tamano=[640, 360])
try:
    menu = MenuPrincipal(vista)
    vista.show_view(menu)
    menu.on_draw()
    clic(vista, next(z for z in vista.lienzo.zonas if z.accion == 'configuracion'), menu)
    ajustes = vista.current_view
    assert isinstance(ajustes, Configuracion)
    ajustes.on_draw()
    zonas_dentro(vista)
    arcade.get_image().save(Path(tempfile.gettempdir()) / 'cripta-configuracion.png')
    x, y = vista.lienzo.a_ventana(ajustes.X + ajustes.ANCHO_SLIDER * 0.7, 297)
    ajustes.on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)
    ajustes.on_mouse_release(x, y, arcade.MOUSE_BUTTON_LEFT, 0)
    assert vista.current_view is ajustes
    assert vista.musica.volumen == 0.7
    ajustes.on_key_press(arcade.key.ESCAPE, 0)
    assert vista.current_view is menu and not app.estado_partida().activa

    assert app.iniciar_partida('Jugador', '42', 'cripta-01').ok
    vista.hide_view()
    antes = firma(app)
    vista.abrir_panel('menu')
    pausa = vista.current_view
    pausa.on_draw()
    zona = next(z for z in vista.lienzo.zonas if z.accion == 'elegir'
                and pausa.opciones[int(z.argumento)][0].startswith('Configuración'))
    clic(vista, zona, pausa)
    ajustes = vista.current_view
    assert isinstance(ajustes, Configuracion)
    ajustes.on_draw()
    x, y = vista.lienzo.a_ventana(ajustes.X + ajustes.ANCHO_SLIDER * 0.6, 215)
    ajustes.on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)
    ajustes.on_mouse_release(x, y, arcade.MOUSE_BUTTON_LEFT, 0)
    assert vista.sonidos.volumen == 0.6 and vista.current_view is ajustes
    with patch('arcade.load_sound'), patch('arcade.play_sound', return_value=SimpleNamespace(volume=0)):
        vista.musica.activo = True
        vista.musica.actual = ''
        vista.musica.poner('cripta')
        vista.musica.cambiar_volumen(0.9)
        assert vista.musica._reproductor.volume == 0.9
        vista.musica._reproductor = None
    for audio in [vista.musica, vista.sonidos]:
        audio.cambiar_volumen(-1)
        assert audio.volumen == 0
        audio.cambiar_volumen(2)
        assert audio.volumen == 1
    ajustes.on_draw()
    x, y = vista.lienzo.a_ventana(ajustes.X + 100, 297)
    ajustes.on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)
    for extremo, esperado in [[ajustes.X - 100, 0], [ajustes.X + ajustes.ANCHO_SLIDER + 100, 1]]:
        x, y = vista.lienzo.a_ventana(extremo, 297)
        ajustes.on_mouse_drag(x, y, 0, 0, arcade.MOUSE_BUTTON_LEFT, 0)
        assert vista.musica.volumen == esperado
    ajustes.on_mouse_release(x, y, arcade.MOUSE_BUTTON_LEFT, 0)
    x, y = vista.lienzo.a_ventana(ajustes.X, 297)
    ajustes.on_mouse_drag(x, y, 0, 0, arcade.MOUSE_BUTTON_LEFT, 0)
    assert vista.musica.volumen == 1
    ajustes.on_key_press(arcade.key.LEFT, 0)
    assert vista.musica.volumen == 0.95
    ajustes.on_key_press(arcade.key.TAB, 0)
    ajustes.on_key_press(arcade.key.HOME, 0)
    assert vista.sonidos.volumen == 0
    ajustes.on_key_press(arcade.key.END, 0)
    assert vista.sonidos.volumen == 1
    ajustes.on_draw()
    clic(vista, next(z for z in vista.lienzo.zonas if z.accion == 'silencio' and z.argumento == '1'), ajustes)
    assert vista.sonidos.activo
    for ancho, alto in [[640, 360], [1100, 740], [1920, 1080]]:
        vista.set_size(ancho, alto)
        ajustes.on_draw()
        zonas_dentro(vista)
    ajustes.on_key_press(arcade.key.ESCAPE, 0)
    assert vista.current_view is None
    assert firma(app) == antes
finally:
    vista.close()
''')


if __name__ == "__main__":
    unittest.main()
