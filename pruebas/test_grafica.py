"""Arcade opcional: animación, interacción y registro con ventana oculta."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


class PruebasGrafica(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("arcade"), "Instalar extra grafica")
    def test_menu_valida_y_abre_partida(self):
        codigo = r'''
import tempfile
from pathlib import Path
from unittest.mock import patch
import arcade
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.grafica import VentanaCripta
from cripta.vista.grafica.menu import MenuPrincipal
from cripta.vista.grafica.carga import PantallaCarga
def avanzar_carga(vista):
    carga = vista.current_view
    assert isinstance(carga, PantallaCarga)
    carga.on_draw()
    carga.on_update(0.1)
    carga.futuro.result(timeout=30)
    carga.on_update(0.1)
with tempfile.TemporaryDirectory() as carpeta:
    app = Aplicacion(AdaptadorOffline('datos_prueba'), carpeta_logs=carpeta)
    vista = VentanaCripta(app, visible=False)
    try:
        menu = MenuPrincipal(vista, 'cripta-stormlight', 'Jugador', '42')
        from threading import Event
        liberar = Event()
        def red_lenta():
            assert liberar.wait(5)
            return 7
        vista.cargar('Conectando', red_lenta, lambda _: vista.show_view(menu))
        carga = vista.current_view
        carga.on_update(0.1)
        assert carga.futuro is None
        carga.on_draw()
        carga.on_update(0.1)
        try:
            for _ in range(5):
                carga.on_update(0.1)
                carga.on_draw()
            assert not carga.futuro.done() and carga.tiempo > 0.5
            arcade.get_image().save(Path(tempfile.gettempdir()) / 'cripta-cargando.png')
            vista.on_close()
            assert vista.current_view is carga
        finally:
            liberar.set()
        carga.futuro.result(timeout=5)
        carga.on_update(0.1)
        def red_fallida():
            raise RuntimeError('Sin conexión')
        vista.cargar('Conectando', red_fallida, lambda _: vista.show_view(menu))
        carga = vista.current_view
        carga.on_draw()
        carga.on_update(0.1)
        try:
            carga.futuro.result(timeout=5)
        except RuntimeError:
            pass
        carga.on_update(0.1)
        assert carga.error == 'Sin conexión'
        carga.on_draw()
        assert len(vista.escena.zonas) == 1
        vista.cargar('Buscando criptas', menu.cargar, lambda _: vista.show_view(menu))
        assert not menu.criptas
        avanzar_carga(vista)
        for w,h in [[640,480],[1100,740]]:
            vista.set_size(w,h)
            menu.ui.on_resize(w, h)
            menu.on_draw()
            for zona in menu.escena.zonas:
                assert 0 <= zona.x and zona.x + zona.ancho <= w
                assert 0 <= zona.y and zona.y + zona.alto <= h
        arcade.get_image().save(Path(tempfile.gettempdir()) / 'cripta-menu.png')
        assert not app.estado_partida().activa
        assert not list(Path(carpeta).glob('*.log'))
        menu.nombre.text = ' '
        from pyglet.event import EventDispatcher
        menu.on_draw()
        zona = next(z for z in menu.escena.zonas if z.accion == 'cripta' and int(z.argumento) == menu.seleccion)
        EventDispatcher.dispatch_event(vista, 'on_mouse_press', zona.x + 5, zona.y + 5, arcade.MOUSE_BUTTON_LEFT, 0)
        assert isinstance(vista.current_view, PantallaCarga)
        assert not app.estado_partida().activa
        avanzar_carga(vista)
        assert isinstance(vista.current_view, PantallaCarga)
        avanzar_carga(vista)
        assert menu.error and not app.estado_partida().activa
        menu.nombre.text = 'Jugador'
        menu.on_draw()
        zona = next(z for z in menu.escena.zonas if z.accion == 'cripta' and int(z.argumento) == menu.seleccion)
        EventDispatcher.dispatch_event(vista, 'on_mouse_press', zona.x + 5, zona.y + 5, arcade.MOUSE_BUTTON_LEFT, 0)
        avanzar_carga(vista)
        avanzar_carga(vista)
        assert app.estado_partida().activa, menu.error
        assert vista.current_view is None
        assert 'OFFLINE' in vista.indicador_red()
        assert f'/{app.estado_partida().presupuesto_solicitudes}' in vista.indicador_red()
        vista.on_draw()
        from cripta.vista.grafica.fin import PantallaFin
        from cripta.estructuras.Bitacora import Mensaje
        p = app.estado_partida()
        p.activa = False
        p.terminada = p.derrota = True
        app.bitacora().append(Mensaje('enemigo', 'El guardián te ataca por 30 de daño.'))
        vista.pausa_visual = vista.duracion_visual = 1.2
        vista.on_update(0.3)
        assert vista.current_view is None
        with patch.object(vista.escena, 'personaje', wraps=vista.escena.personaje) as dibujar:
            vista.on_draw()
            cuadros = vista.escena.recursos.soldado_morir
            assert dibujar.call_args.args[0] is cuadros[min(len(cuadros) - 1, int(0.25 * len(cuadros)))]
        vista.on_update(0.4)
        assert vista.current_view is None
        vista.on_update(0.6)
        assert isinstance(vista.current_view, PantallaFin)
        assert 'guardián' in vista.current_view.mensajes[-1]
        assert not vista.current_view.puntajes
        from cripta.adaptadores.Puntajes import Puntaje
        from unittest.mock import patch
        registros = [Puntaje(str(i), f'Jugador {i}', 'cripta-stormlight', '1', i, i, i * 100,
                             'victoria' if i % 2 else 'derrota') for i in range(20)]
        with patch.object(app, 'puntajes', return_value=registros) as leer:
            vista.show_view(PantallaFin(vista))
            for _ in range(3):
                vista.current_view.on_draw()
            leer.assert_called_once()
        for victoria in [False, True]:
            p.victoria = victoria
            p.derrota = not victoria
            for w, h in [[640, 480], [1100, 740]]:
                vista.set_size(w, h)
                vista.current_view.on_draw()
                assert len(vista.escena.zonas) == 3
                assert all(0 <= z.x and z.x + z.ancho <= w and 0 <= z.y and z.y + z.alto <= h
                           for z in vista.escena.zonas)
                assert vista.current_view.puntajes == registros
                vista.current_view.on_mouse_scroll(300, 200, 0, -100)
                assert vista.current_view.desplazamiento == vista.current_view.limite
                vista.current_view.on_draw()
                assert any(t.text == 'Jugador 19' for t in vista.escena.textos[:vista.escena.texto_actual])
                vista.current_view.on_mouse_scroll(300, 200, 0, 100)
                assert vista.current_view.desplazamiento == 0
                vista.current_view.on_draw()
            arcade.get_image().save(Path(tempfile.gettempdir()) / ('cripta-victoria.png' if victoria else 'cripta-muerte.png'))
        with patch.object(app, 'puntajes', side_effect=ValueError('Tabla inválida')):
            error = PantallaFin(vista)
            assert error.error == 'Tabla inválida' and not error.puntajes
            error.on_draw()
        vista.current_view.ejecutar('reintentar')
        avanzar_carga(vista)
        assert vista.current_view is None and app.estado_partida().activa
        app.terminar()
        vista.on_update(1)
        vista.current_view.ejecutar('menu')
        avanzar_carga(vista)
        assert isinstance(vista.current_view, MenuPrincipal)
        vista.current_view.on_draw()
        vista.current_view.comenzar()
        avanzar_carga(vista)
        assert vista.current_view is None and app.estado_partida().activa
        vista.on_close()
    finally:
        vista.close()
'''
        resultado = subprocess.run([sys.executable, "-B", "-c", codigo],
                                   cwd=Path(__file__).resolve().parents[1],
                                   capture_output=True, text=True, timeout=60)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)

    @unittest.skipUnless(importlib.util.find_spec("arcade"), "Instalar extra grafica")
    def test_animaciones_no_avanzan_simulacion_y_acciones_reales(self):
        codigo = r'''
import tempfile
import warnings
from pathlib import Path
import arcade
from arcade.exceptions import PerformanceWarning
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.grafica import VentanaCripta
from cripta.vista.grafica.escena import lineas_bitacora
from types import SimpleNamespace
from cripta.replay.reproductor import reproducir
from pruebas.test_replay import FuenteReplay, firma

with tempfile.TemporaryDirectory() as carpeta:
    app = Aplicacion(FuenteReplay(), carpeta_logs=carpeta)
    assert app.iniciar_partida('Jugador', '42', 'cripta-01').ok
    vista = VentanaCripta(app, visible=False)
    try:
        warnings.simplefilter('error', PerformanceWarning)
        antes = firma(app)
        for _ in range(120):
            vista.on_update(1 / 60)
        assert firma(app) == antes
        mensaje = 'Una puerta cerrada necesita la llave correcta para poder abrirse.'
        lineas = lineas_bitacora([mensaje], 18)
        assert all(len(linea) <= 18 for linea in lineas)
        assert ' '.join(lineas) == mensaje
        vista.escena.bitacora(vista, [mensaje] * 20, 455, 185, 480)
        assert vista.bitacora_limite > 19
        vista.on_mouse_scroll(450, 170, 0, 1000)
        assert vista.bitacora_desplazamiento == vista.bitacora_limite
        vista.on_mouse_scroll(450, 170, 0, -1000)
        assert vista.bitacora_desplazamiento == 0
        vista.on_draw()
        etiquetas = list(vista.escena.textos)
        vista.on_draw()
        assert len(vista.escena.textos) == len(etiquetas)
        assert all(a is b for a, b in zip(etiquetas, vista.escena.textos))
        objetos = [[z.argumento, z.x, z.y, z.ancho, z.alto] for z in vista.zonas if z.accion == 'recoger']
        antes = firma(app)
        vista.on_update(0.5)
        vista.on_draw()
        assert objetos == [[z.argumento, z.x, z.y, z.ancho, z.alto] for z in vista.zonas if z.accion == 'recoger']
        assert firma(app) == antes
        recursos = vista.escena.recursos
        assert not Path('src/cripta/vista/recursos/0x72').exists()
        assert recursos.enemigo(SimpleNamespace(tipo='oseo', nombre='Guardián óseo')) is next(c for n, c in recursos.personajes if n == 'Demon_A')
        from unittest.mock import patch
        from cripta.vista.grafica.recursos import Recursos
        with patch('cripta.vista.grafica.packs.LOCAL', Path(carpeta) / 'sin_packs'):
            alternativa = Recursos()
            assert all(t.image.getbbox() for t in [alternativa.estatua, alternativa.objeto, alternativa.antidoto,
                                                  alternativa.cofre, alternativa.caja, alternativa.espada])
        if recursos.soldado_idle and recursos.soldado_atacar:
            assert all(t.width == recursos.soldado_idle[0].width and t.height == recursos.soldado_idle[0].height
                       for t in recursos.soldado_idle + recursos.soldado_correr + recursos.soldado_atacar + recursos.soldado_herido + recursos.soldado_morir)
        for nombre, cuadros in recursos.personajes:
            ataques = next(c for n, c in recursos.ataques if n == nombre)
            if cuadros and ataques:
                assert all(t.width == cuadros[0].width and t.height == cuadros[0].height for t in ataques)
        assert recursos.icono(SimpleNamespace(tipo_id='itm_daga_oxidada', nombre='Daga')) is recursos.daga
        assert recursos.icono(SimpleNamespace(tipo_id='itm_pocion_menor', nombre='Poción')) is recursos.objeto
        assert recursos.icono(SimpleNamespace(tipo_id='itm_antidoto', nombre='Antídoto')) is recursos.antidoto
        for capacidad in [8, 12]:
            inv = SimpleNamespace(capacidad=capacidad, tamano=capacidad,
                                  items=lambda: [SimpleNamespace(instancia_id=str(i), clase='arma',
                                                                 tipo_id='daga', nombre='Daga', equipado=False)
                                                 for i in range(capacidad)], buscar_por_id=lambda id_: None)
            vista.escena.zonas = []
            vista.escena.inventario(vista, inv, 455, 185, 480)
            zonas = [z for z in vista.escena.zonas if z.accion == 'seleccionar_item']
            assert len(zonas) == capacidad
            assert len([z for z in zonas if z.y == zonas[0].y]) == 4
            assert all(455 <= z.x and z.x + z.ancho <= 640 for z in zonas)
            assert all(z.y > 480 - 215 for z in zonas)
        antes = firma(app)
        vista.on_mouse_motion(25, 25, 0, 0)
        vista.on_draw()
        assert vista.escena.raton == [25, 25]
        assert firma(app) == antes
        from cripta.vista.grafica.panel import Panel
        for accion in ['ayuda', 'informacion', 'terminar']:
            vista.ejecutar(accion)
            assert isinstance(vista.current_view, Panel)
            vista.current_view.on_draw()
            vista.current_view.on_mouse_scroll(30, 200, 0, -2)
            vista.current_view.on_key_press(arcade.key.ESCAPE, 0)
            assert firma(app) == antes
        vista.on_mouse_motion(0, 0, 0, 0)
        for accion in ['atacar', 'mover', 'abrir', 'recoger', 'usar', 'equipar', 'soltar']:
            vista.ejecutar(accion)
            assert vista.current_view is None
            assert firma(app) == antes
        for _ in range(4):
            vista.ejecutar('ordenar')
            vista.on_draw()
            assert firma(app) == antes
        assert vista.criterio == 'real'
        vecina = app.estado_partida().vecindad[0]
        cerrada = vecina.cerrada
        vecina.cerrada = True
        vista.ejecutar('mover_mapa', vecina.direccion)
        vecina.cerrada = cerrada
        assert firma(app) == antes
        vista.on_draw()
        objeto = next(z for z in vista.zonas if z.accion == 'recoger' and z.argumento == 'sala-1-objeto-9')
        vista.on_mouse_motion(objeto.x + 5, objeto.y + 5, 0, 0)
        vista.on_key_press(arcade.key.R, 0)
        assert vista.current_view is None
        vista.on_update(1)
        vista.on_draw()
        item = next(z for z in vista.zonas if z.accion == 'seleccionar_item')
        antes = firma(app)
        vista.on_mouse_press(item.x + 5, item.y + 5, arcade.MOUSE_BUTTON_LEFT, 0)
        assert firma(app) == antes
        vista.on_key_press(arcade.key.E, 0)
        assert app.inventario().buscar_por_id(vista.item).equipado
        vista.on_update(1)
        vista.ejecutar('informacion')
        vista.current_view.on_draw()
        assert 'peso' in vista.current_view.texto
        vista.current_view.on_key_press(arcade.key.ESCAPE, 0)
        vista.on_key_press(arcade.key.D, 0)
        assert app.inventario().buscar_por_id(vista.item) is None
        vista.on_update(1)
        vista.ejecutar('recoger', 'sala-1-objeto-8')
        vista.on_update(1)
        vista.on_draw()
        puerta = next(z for z in vista.zonas if z.accion == 'mover_mapa')
        vista.on_mouse_press(puerta.x + 10, puerta.y + 10, arcade.MOUSE_BUTTON_LEFT, 0)
        assert app.estado_partida().sala_actual_id == 2
        assert 'rata' in vista.atacantes
        assert vista.dano_visual > 0
        assert vista.pausa_visual == 0.65
        antes_orientacion = firma(app)
        escena = vista.escena
        for x, izquierda in [[30, False], [400, True]]:
            with patch.object(escena.distribucion, 'posicion', return_value=[x, 200]), \
                 patch.object(escena.recursos, 'enemigo', wraps=escena.recursos.enemigo) as elegir, \
                 patch.object(escena, 'personaje', wraps=escena.personaje) as dibujar:
                escena.enemigos(vista, app.estado_partida(), 20, 155, 500, 300, 0)
                assert any(c.kwargs.get('atacar') and c.kwargs.get('izquierda') == izquierda for c in elegir.call_args_list)
                assert dibujar.call_args.kwargs['izquierda'] == izquierda
                assert list(dibujar.call_args.args[2:4]) == [x, 200]
            assert firma(app) == antes_orientacion
        antes = firma(app)
        vista.on_update(0.3)
        vista.on_draw()
        assert firma(app) == antes
        vista.on_update(1)
        vista.on_draw()
        enemigo = next(z for z in vista.zonas if z.accion == 'seleccionar')
        antes = firma(app)
        with patch('cripta.vista.grafica.ventana.monotonic', return_value=1):
            vista.on_mouse_press(enemigo.x + 5, enemigo.y + 5, arcade.MOUSE_BUTTON_LEFT, 0)
        assert vista.enemigo == 'rata'
        assert firma(app) == antes
        with patch('cripta.vista.grafica.ventana.monotonic', return_value=2):
            vista.on_mouse_press(enemigo.x + 5, enemigo.y + 5, arcade.MOUSE_BUTTON_LEFT, 0)
        assert firma(app) == antes
        with patch('cripta.vista.grafica.ventana.monotonic', return_value=2.2):
            vista.on_mouse_press(enemigo.x + 5, enemigo.y + 5, arcade.MOUSE_BUTTON_LEFT, 0)
        assert app.estado_partida().acciones_ejecutadas == 6
        assert vista.ultimo_click is None
        despues = firma(app)
        vista.on_mouse_press(enemigo.x + 5, enemigo.y + 5, arcade.MOUSE_BUTTON_LEFT, 0)
        assert firma(app) == despues
        assert vista.accion_visual == 'atacar' and vista.pausa_visual == 0.65
        assert any(cambio < 0 for id_, cambio in vista.cambios_enemigos)
        antes_orientacion = firma(app)
        for accion in ['', 'atacar']:
            vista.accion_visual = accion
            for x, izquierda in [[30, True], [400, False]]:
                with patch.object(vista.escena.distribucion, 'posicion', return_value=[x, 200]), \
                     patch.object(vista.escena, 'personaje', wraps=vista.escena.personaje) as dibujar:
                    vista.escena.jugador(vista, app.estado_partida(), 20, 155, 500, 300, 0)
                    assert dibujar.call_args.kwargs['izquierda'] == izquierda
                    assert list(dibujar.call_args.args[2:6]) == [190, 290, 39, 72]
                    estado = 2 if accion else 3 if vista.cambio_vida < 0 or vista.atacantes else 0
                    cuadros = recursos.soldado_izquierda[estado] if izquierda else [recursos.soldado_idle, recursos.soldado_correr, recursos.soldado_atacar, recursos.soldado_herido][estado]
                    assert dibujar.call_args.args[0] is cuadros[0]
                assert firma(app) == antes_orientacion
        vista.on_update(0.4)
        with patch.object(recursos, 'enemigo', wraps=recursos.enemigo) as elegir:
            vista.on_draw()
            assert any(c.kwargs.get('estado') == 'herido' for c in elegir.call_args_list)
        assert firma(app) == antes_orientacion
        vista.on_update(1)
        vista.ejecutar('seleccionar_item', 'sala-1-objeto-8')
        vista.on_key_press(arcade.key.U, 0)
        assert app.inventario().buscar_por_id('sala-1-objeto-8') is None
        assert vista.cambio_vida > 0
        assert firma(reproducir(app._partida.registro.ruta, [FuenteReplay()])) == firma(app)
        antes_muerte = firma(app)
        vista.enemigos_muertos = [SimpleNamespace(id='caido', tipo='orco', nombre='Orco caído')]
        vista.pausa_visual = vista.duracion_visual = 1.2
        with patch.object(vista.escena.distribucion, 'posicion', return_value=[300, 230]), \
             patch.object(recursos, 'enemigo', wraps=recursos.enemigo) as elegir:
            vista.on_draw()
            assert any(c.kwargs.get('estado') == 'muerto' for c in elegir.call_args_list)
            assert not any(z.accion == 'seleccionar' and z.argumento == 'caido' for z in vista.zonas)
            vista.on_update(0.6)
            vista.on_draw()
            arcade.get_image().save(Path(tempfile.gettempdir()) / 'cripta-enemigo-muerte.png')
            vista.on_update(0.7)
            elegir.reset_mock()
            vista.on_draw()
            assert not any(c.kwargs.get('estado') == 'muerto' for c in elegir.call_args_list)
        assert firma(app) == antes_muerte
        vista.enemigos_muertos = []
        for ancho, alto in [[640, 480], [1100, 740]]:
            vista.set_size(ancho, alto)
            vista.on_draw()
            for zona in vista.zonas:
                assert 0 <= zona.x and zona.x + zona.ancho <= ancho
                assert 0 <= zona.y and zona.y + zona.alto <= alto
                if zona.accion == 'mover_mapa':
                    assert zona.y + zona.alto < 155
            arcade.get_image().save(Path(tempfile.gettempdir()) / f'cripta-mapa-{ancho}.png')
        from pyglet.event import EventDispatcher
        antes = firma(app)
        EventDispatcher.dispatch_event(vista, 'on_key_press', arcade.key.ESCAPE, 0)
        assert isinstance(vista.current_view, Panel)
        assert firma(app) == antes
        EventDispatcher.dispatch_event(vista, 'on_key_press', arcade.key.ESCAPE, 0)
        assert vista.current_view is None and firma(app) == antes
        EventDispatcher.dispatch_event(vista, 'on_key_press', arcade.key.ESCAPE, 0)
        vista.current_view.on_draw()
        confirmar = next(z for z in vista.escena.zonas if z.accion == 'elegir')
        EventDispatcher.dispatch_event(vista, 'on_mouse_press', confirmar.x + 5, confirmar.y + 5, arcade.MOUSE_BUTTON_LEFT, 0)
        assert app.estado_partida().terminada
    finally:
        vista.close()
'''
        resultado = subprocess.run([sys.executable, "-B", "-c", codigo],
                                   cwd=Path(__file__).resolve().parents[1],
                                   capture_output=True, text=True, timeout=60)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)

    def test_grafica_en_red_usa_adaptador_existente(self):
        from unittest.mock import patch
        from cripta.bootstrap import main
        with patch('cripta.bootstrap.NetworkAdapter') as red, patch('cripta.vista.grafica.iniciar', return_value=0) as iniciar:
            self.assertEqual(main(["--grafica"]), 0)
            red.assert_called_once()
            self.assertFalse(iniciar.call_args.args[-1])
