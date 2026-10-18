"""Arcade opcional: animación, interacción, escalado y registro con ventana oculta."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


def _ejecutar(prueba, codigo):
    resultado = subprocess.run([sys.executable, "-B", "-c", codigo],
                               cwd=Path(__file__).resolve().parents[1],
                               capture_output=True, text=True, timeout=120)
    prueba.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)


COMUN = r'''
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import arcade
from cripta.vista.grafica import VentanaCripta
from cripta.vista.grafica.carga import PantallaCarga
from cripta.vista.grafica.medidas import ALTO, ANCHO

def clic(vista, zona, destino=None):
    """Clic real en coordenadas de la ventana sobre una zona virtual."""
    x, y = vista.lienzo.a_ventana(zona.x + 3, zona.y + 3)
    (destino or vista).on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)

def mover_raton(vista, zona, destino=None):
    x, y = vista.lienzo.a_ventana(zona.x + 3, zona.y + 3)
    (destino or vista).on_mouse_motion(x, y, 0, 0)

def zonas_dentro(vista):
    for zona in vista.lienzo.zonas:
        assert 0 <= zona.x and zona.x + zona.ancho <= ANCHO, zona
        assert 0 <= zona.y and zona.y + zona.alto <= ALTO, zona
        x0, y0 = vista.lienzo.a_ventana(zona.x, zona.y)
        x1, y1 = vista.lienzo.a_ventana(zona.x + zona.ancho, zona.y + zona.alto)
        assert -1 <= x0 and x1 <= vista.width + 1 and -1 <= y0 and y1 <= vista.height + 1, zona

def avanzar_carga(vista):
    carga = vista.current_view
    assert isinstance(carga, PantallaCarga)
    carga.on_draw()
    carga.on_update(0.1)
    carga.futuro.result(timeout=30)
    carga.on_update(0.1)
'''


class PruebasGrafica(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("arcade"), "Falta arcade (uv sync)")
    def test_continuar_y_confirmar_reemplazo(self):
        """Continuar carga el guardado; cancelar conserva la partida en curso."""
        _ejecutar(self, COMUN + r'''
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.grafica.menu import MenuPrincipal
from cripta.vista.grafica.panel import Panel
from pruebas.test_replay import FuenteReplay
from pruebas.test_guardado import preparar_partida, huella
from pyglet.event import EventDispatcher
with tempfile.TemporaryDirectory() as carpeta:
    ruta = Path(carpeta) / 'partida.bin'
    app = Aplicacion(FuenteReplay(), ruta_guardado=ruta, carpeta_logs=Path(carpeta) / 'sesion')
    vista = VentanaCripta(app, visible=False, tamano=[1100, 620])
    try:
        menu = MenuPrincipal(vista)
        vista.show_view(menu)
        menu.on_draw()
        zonas_dentro(vista)
        arcade.get_image().save(Path(tempfile.gettempdir()) / 'cripta-continuar.png')
        continuar = next(z for z in vista.lienzo.zonas if z.accion == 'continuar')
        clic(vista, continuar, menu)
        avanzar_carga(vista)
        selector = vista.current_view
        assert isinstance(selector, Panel) and not selector.opciones
        selector.on_draw()
        EventDispatcher.dispatch_event(vista, 'on_key_press', arcade.key.ESCAPE, 0)
        assert vista.current_view is menu
        assert not app.estado_partida().activa

        guardada = preparar_partida(ruta)
        assert guardada.guardar().ok
        esperado = huella(guardada)
        segunda = Path(carpeta) / 'sesion' / 'guardadas' / 'ana.bin'
        ana = Aplicacion(FuenteReplay(), ruta_guardado=segunda)
        assert ana.iniciar_partida('Ana', '33', 'cripta-01').ok
        assert ana.guardar().ok
        menu.on_draw()
        continuar = next(z for z in vista.lienzo.zonas if z.accion == 'continuar')
        clic(vista, continuar, menu)
        assert isinstance(vista.current_view, PantallaCarga)
        avanzar_carga(vista)
        selector = vista.current_view
        assert isinstance(selector, Panel) and len(selector.opciones) == 2
        selector.on_draw()
        arcade.get_image().save(Path(tempfile.gettempdir()) / 'cripta-elegir-guardado.png')
        zonas_dentro(vista)
        elegir = next(z for z in vista.lienzo.zonas if z.accion == 'elegir'
                      and selector.opciones[int(z.argumento)][0].startswith('Jugador'))
        clic(vista, elegir, selector)
        avanzar_carga(vista)
        assert vista.current_view is None and huella(app) == esperado
        assert vista.item == app.inventario().item_actual().instancia_id

        assert app.esperar().ok
        antes = huella(app)
        with patch.object(app, 'cargar', wraps=app.cargar) as cargar:
            vista.cargar_partida()
            assert isinstance(vista.current_view, Panel)
            EventDispatcher.dispatch_event(vista, 'on_key_press', arcade.key.ESCAPE, 0)
            assert vista.current_view is None and huella(app) == antes
            vista.cargar_partida()
            panel = vista.current_view
            panel.on_draw()
            cancelar = next(z for z in vista.lienzo.zonas if z.accion == 'elegir'
                            and int(z.argumento) == 0)
            clic(vista, cancelar, panel)
            assert vista.current_view is None and huella(app) == antes
            cargar.assert_not_called()

        vista.cargar_partida()
        panel = vista.current_view
        panel.on_draw()
        confirmar = next(z for z in vista.lienzo.zonas if z.accion == 'elegir'
                         and int(z.argumento) == 1)
        clic(vista, confirmar, panel)
        avanzar_carga(vista)
        assert vista.current_view is None and huella(app) == esperado
        assert vista.item == app.inventario().item_actual().instancia_id

        ruta.write_bytes(b'guardado incompleto')
        antes = huella(app)
        vista.cargar_partida(confirmar=False)
        avanzar_carga(vista)
        assert vista.current_view is None and huella(app) == antes
        assert vista.mensaje
        vista.on_draw()
        vista.elegir_guardado()
        avanzar_carga(vista)
        selector = vista.current_view
        selector.on_draw()
        elegir = next(z for z in vista.lienzo.zonas if z.accion == 'elegir'
                      and selector.opciones[int(z.argumento)][0].startswith('Ana'))
        clic(vista, elegir, selector)
        assert isinstance(vista.current_view, Panel)
        panel = vista.current_view
        panel.on_draw()
        confirmar = next(z for z in vista.lienzo.zonas if z.accion == 'elegir' and int(z.argumento) == 1)
        clic(vista, confirmar, panel)
        avanzar_carga(vista)
        assert vista.current_view is None and app.estado_partida().nombre_jugador == 'Ana'
        tiempo = app.estado_partida().reloj_virtual
        ataque = app.estado_partida().jugador_ataque
        vista.ejecutar('cheats')
        panel = vista.current_view
        panel.on_draw()
        aumentar = next(z for z in vista.lienzo.zonas if z.accion == 'elegir' and int(z.argumento) == 1)
        clic(vista, aumentar, panel)
        assert vista.current_view is None and app.trucos_activos
        assert app.estado_partida().jugador_ataque == ataque + 50
        assert app.estado_partida().reloj_virtual == tiempo
        assert 'CHEATS' in vista.indicador_red()
        vista.ejecutar('cheats')
        panel = vista.current_view
        assert len(panel.opciones) == 7
        panel.on_draw()
        zonas_dentro(vista)
        activar = next(z for z in vista.lienzo.zonas if z.accion == 'elegir' and int(z.argumento) == 3)
        clic(vista, activar, panel)
        assert app.truco_activo('god_mode')
        vista.ejecutar('cheats')
        panel = vista.current_view
        assert any('God Mode: ON' in opcion[0] for opcion in panel.opciones)
        panel.on_draw()
        arcade.get_image().save(Path(tempfile.gettempdir()) / 'cripta-cheats.png')
        activar = next(z for z in vista.lienzo.zonas if z.accion == 'elegir' and int(z.argumento) == 4)
        clic(vista, activar, panel)
        assert app.truco_activo('insta_kill')

        from pruebas.test_guardados import AdaptadorOffline as FuenteLocal
        local = Aplicacion(FuenteLocal(), ruta_guardado=Path(carpeta) / 'offline.bin')
        assert local.iniciar_partida('Local', '42', 'cripta-custom').ok
        assert local.guardar().ok
        with patch('cripta.controlador.GuardadoControlador.AdaptadorOffline', return_value=FuenteLocal()), \
             patch('cripta.controlador.GuardadoControlador.NetworkAdapter') as red:
            vista.cargar_partida(confirmar=False, ruta=local.ruta_guardado)
            avanzar_carga(vista)
            red.assert_not_called()
        assert vista.current_view is None and vista.controlador is not app
        assert vista.controlador.estado_partida().nombre_jugador == 'Local'
        assert vista.modo == 'OFFLINE' and not vista.controlador.trucos_activos
        vista.on_draw()
    finally:
        vista.close()
''')

    @unittest.skipUnless(importlib.util.find_spec("arcade"), "Falta arcade (uv sync)")
    def test_menu_carga_fin_y_escalado(self):
        _ejecutar(self, COMUN + r'''
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.grafica.menu import MenuPrincipal
from cripta.vista.grafica.fin import PantallaFin
from cripta.estructuras.Bitacora import Mensaje
from cripta.adaptadores.Puntajes import Puntaje
from threading import Event
with tempfile.TemporaryDirectory() as carpeta:
    app = Aplicacion(AdaptadorOffline('datos_prueba'), carpeta_logs=carpeta)
    vista = VentanaCripta(app, visible=False, tamano=[1100, 620])
    try:
        menu = MenuPrincipal(vista, 'cripta-stormlight', 'Jugador', '42')
        liberar = Event()
        def red_lenta():
            assert liberar.wait(5)
            return 7
        vista.cargar('Conectando', red_lenta, lambda _: vista.show_view(menu))
        carga = vista.current_view
        carga.on_update(0.1)
        assert carga.futuro is None          # primero se dibuja, después trabaja
        carga.on_draw()
        carga.on_update(0.1)
        try:
            for _ in range(5):
                carga.on_update(0.1)
                carga.on_draw()
            assert not carga.futuro.done() and carga.tiempo > 0.5
            vista.on_close()
            assert vista.current_view is carga  # no se cierra en medio de una carga
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
        assert [z.accion for z in vista.lienzo.zonas] == ['reintentar']
        vista.cargar('Buscando criptas', menu.cargar, lambda _: vista.show_view(menu))
        assert not menu.criptas
        avanzar_carga(vista)
        assert vista.current_view is menu
        for w, h in [[640, 360], [1100, 620], [1366, 705], [1600, 900]]:
            vista.set_size(w, h)
            menu.on_draw()
            zonas_dentro(vista)
        assert not app.estado_partida().activa
        assert not list(Path(carpeta).glob('*.log'))
        # Nombre vacío: el controlador rechaza y se vuelve al menú con el motivo.
        menu.nombre.text = ''
        menu.on_text('  ')
        menu.on_draw()
        zona = next(z for z in vista.lienzo.zonas if z.accion == 'iniciar')
        clic(vista, zona, menu)
        avanzar_carga(vista)
        assert vista.current_view is menu and menu.error and not app.estado_partida().activa
        # Campo propio: escribir, borrar y semilla solo con dígitos.
        menu.foco = menu.nombre
        menu.nombre.text = ''
        menu.on_text('Jugadora')
        menu.on_key_press(arcade.key.BACKSPACE, 0)
        assert menu.nombre.text == 'Jugador'
        menu.on_key_press(arcade.key.TAB, 0)
        menu.semilla.text = ''
        menu.on_text('4x2')
        assert menu.semilla.text == '42'
        menu.on_draw()
        zona = next(z for z in vista.lienzo.zonas if z.accion == 'cripta' and int(z.argumento) == menu.seleccion)
        clic(vista, zona, menu)              # elegir una cripta solo carga sus datos
        avanzar_carga(vista)
        assert vista.current_view is menu and not app.estado_partida().activa
        menu.on_key_press(arcade.key.ENTER, 0)
        avanzar_carga(vista)
        assert app.estado_partida().activa, menu.error
        assert vista.current_view is None
        assert 'OFFLINE' in vista.indicador_red()
        assert f'/{app.estado_partida().presupuesto_solicitudes}' in vista.indicador_red()
        vista.on_draw()
        p = app.estado_partida()
        p.activa = False
        p.terminada = p.derrota = True
        app.bitacora().append(Mensaje('enemigo', 'El guardián te ataca por 30 de daño.'))
        vista.pausa_visual = vista.duracion_visual = 1.2
        vista.on_update(0.3)
        assert vista.current_view is None    # primero se anima la muerte
        with patch.object(vista.escena, 'personaje', wraps=vista.escena.personaje) as dibujar:
            vista.on_draw()
            cuadros = vista.escena.recursos.heroe(*vista.escena.equipo_jugador(p))[4]
            assert dibujar.call_args.args[0] is cuadros[min(len(cuadros) - 1, int(0.25 * len(cuadros)))]
        vista.on_update(0.4)
        assert vista.current_view is None
        vista.on_update(0.6)
        assert isinstance(vista.current_view, PantallaFin)
        assert 'guardián' in vista.current_view.mensajes[-1]
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
            for w, h in [[640, 360], [1600, 900]]:
                vista.set_size(w, h)
                vista.current_view.on_draw()
                assert [z.accion for z in vista.lienzo.zonas] == ['reintentar', 'menu', 'salir']
                zonas_dentro(vista)
                vista.current_view.on_mouse_scroll(300, 200, 0, -100)
                assert vista.current_view.desplazamiento == vista.current_view.limite
                vista.current_view.on_draw()
                assert any(t.text == 'Jugador 19' for t in vista.lienzo.textos[:vista.lienzo.texto_actual])
                vista.current_view.on_mouse_scroll(300, 200, 0, 100)
                assert vista.current_view.desplazamiento == 0
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
''')

    @unittest.skipUnless(importlib.util.find_spec("arcade"), "Falta arcade (uv sync)")
    def test_animaciones_no_avanzan_simulacion_y_acciones_reales(self):
        _ejecutar(self, COMUN + r'''
import warnings
from arcade.exceptions import PerformanceWarning
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.grafica import fuente_pixel as fp
from cripta.vista.grafica.escena import lineas_bitacora, PANEL_X, PANEL_ANCHO
from cripta.vista.grafica.panel import Panel
from cripta.replay.reproductor import reproducir
from pruebas.test_replay import FuenteReplay, firma

with tempfile.TemporaryDirectory() as carpeta:
    app = Aplicacion(FuenteReplay(), carpeta_logs=carpeta)
    assert app.iniciar_partida('Jugador', '42', 'cripta-01').ok
    vista = VentanaCripta(app, visible=False, tamano=[1600, 900])
    try:
        warnings.simplefilter('error', PerformanceWarning)
        antes = firma(app)
        for _ in range(120):
            vista.on_update(1 / 60)
        assert firma(app) == antes
        mensaje = 'Una puerta cerrada necesita la llave correcta para poder abrirse.'
        lineas = lineas_bitacora([mensaje], 90)
        assert all(fp.ancho_texto(linea) <= 90 for linea in lineas)
        assert ' '.join(lineas) == mensaje
        vista.escena.bitacora(vista, [mensaje] * 20)
        assert vista.bitacora_limite > 19
        x, y = vista.lienzo.a_ventana(PANEL_X + 20, 150)
        vista.on_mouse_scroll(x, y, 0, 1000)
        assert vista.bitacora_desplazamiento == vista.bitacora_limite
        vista.on_mouse_scroll(x, y, 0, -1000)
        assert vista.bitacora_desplazamiento == 0
        vista.on_draw()
        etiquetas = list(vista.lienzo.textos)
        vista.on_draw()
        assert len(vista.lienzo.textos) == len(etiquetas)              # se reutilizan
        assert all(a is b for a, b in zip(etiquetas, vista.lienzo.textos))
        objetos = [[z.argumento, z.x, z.y, z.ancho, z.alto] for z in vista.zonas if z.accion == 'recoger']
        antes = firma(app)
        vista.on_update(0.5)
        vista.on_draw()
        assert objetos == [[z.argumento, z.x, z.y, z.ancho, z.alto] for z in vista.zonas if z.accion == 'recoger']
        assert firma(app) == antes
        recursos = vista.escena.recursos
        assert recursos.nombre_enemigo(SimpleNamespace(tipo='ent_guardian_oseo', nombre='Guardián óseo')) == 'Esqueleto'
        assert vista.pista_actual() in ['cripta', 'combate']            # música de la partida
        equipado = recursos.heroe('itm_daga_oxidada Daga oxidada', 'itm_coraza_cuero Coraza de cuero', True)
        assert len(equipado) == 5 and equipado is recursos.heroe('daga', 'cuero', True)
        assert equipado is not recursos.heroe()                         # sin equipo es otro sprite
        assert recursos.nombre_enemigo(SimpleNamespace(tipo='ent_rata_gigante', nombre='Rata gigante')) == 'Rata'
        assert recursos.nombre_enemigo(SimpleNamespace(tipo='sl_acechador_grietas', nombre='Acechador')) == 'Orc'
        # Respaldo: un tipo desconocido usa el espectro de su comportamiento.
        assert recursos.nombre_enemigo(SimpleNamespace(tipo='ent_nuevo', nombre='Cosa', comportamiento='errante')) == 'Espectro errante'
        assert recursos.nombre_enemigo(SimpleNamespace(tipo='ent_nuevo', nombre='Cosa', comportamiento='')) == 'Espectro '
        assert recursos.enemigo(SimpleNamespace(tipo='ent_guardian_oseo', nombre='Guardián óseo')) is next(c for n, c in recursos.personajes if n == 'Esqueleto')
        from cripta.vista.grafica.recursos import Recursos
        with patch('cripta.vista.grafica.packs.LOCAL', Path(carpeta) / 'sin_packs'):
            alternativa = Recursos()                                   # sin packs: no falla
            assert alternativa.heroe() and alternativa.espada
            # Sin packs, los tipos de los packs caen al espectro según su comportamiento.
            assert alternativa.nombre_enemigo(SimpleNamespace(tipo='sl_acechador_grietas', nombre='Acechador', comportamiento='rastreador')) == 'Espectro rastreador'
            assert alternativa.enemigo(SimpleNamespace(tipo='ent_rata_gigante', nombre='Rata gigante'))
        assert recursos.icono(SimpleNamespace(tipo_id='itm_daga_oxidada', nombre='Daga')) is recursos.daga
        assert recursos.icono(SimpleNamespace(tipo_id='itm_pocion_menor', nombre='Poción')) is recursos.pocion_roja
        assert recursos.icono(SimpleNamespace(tipo_id='itm_antidoto', nombre='Antídoto')) is recursos.antidoto
        assert recursos.icono(SimpleNamespace(tipo_id='sl_luz_tormentosa', nombre='Dosis de luz tormentosa')) is recursos.pocion_roja
        for capacidad in [8, 12, 20]:
            inv = SimpleNamespace(capacidad=capacidad, tamano=capacidad, buscar_por_id=lambda id_: None,
                                  items=lambda: [SimpleNamespace(instancia_id=str(i), clase='arma', peso=1, valor=1,
                                                                 tipo_id='daga', nombre='Daga', equipado=False)
                                                 for i in range(capacidad)])
            vista.lienzo.zonas = []
            vista.escena.inventario(vista, inv)
            zonas = [z for z in vista.lienzo.zonas if z.accion == 'seleccionar_item']
            assert len(zonas) == capacidad
            assert len([z for z in zonas if z.y == zonas[0].y]) == (4 if capacidad <= 12 else 5)
            assert all(PANEL_X <= z.x and z.x + z.ancho <= PANEL_X + PANEL_ANCHO for z in zonas)
        antes = firma(app)
        vista.on_mouse_motion(25, 25, 0, 0)
        vista.on_draw()
        assert vista.raton == vista.lienzo.a_virtual(25, 25)
        assert firma(app) == antes
        for accion in ['ayuda', 'informacion', 'terminar', 'menu']:
            vista.ejecutar(accion)
            assert isinstance(vista.current_view, Panel)
            vista.current_view.on_draw()
            vista.current_view.on_mouse_scroll(30, 200, 0, -2)
            vista.current_view.on_key_press(arcade.key.ESCAPE, 0)
            assert vista.current_view is None
            assert firma(app) == antes
        vista.on_mouse_motion(0, 0, 0, 0)
        for accion in ['atacar', 'mover', 'abrir', 'recoger', 'usar', 'equipar', 'soltar']:
            vista.ejecutar(accion)
            assert vista.current_view is None
            assert firma(app) == antes
        vista.ejecutar('modo_mover')
        assert vista.modo_mover
        vista.on_draw()
        vista.on_key_press(arcade.key.ESCAPE, 0)
        assert not vista.modo_mover and vista.current_view is None and firma(app) == antes
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
        mover_raton(vista, objeto)
        vista.on_key_press(arcade.key.R, 0)                      # recoger lo que está bajo el cursor
        assert app.inventario().buscar_por_id('sala-1-objeto-9') is not None
        vista.on_update(1)
        vista.on_draw()
        item = next(z for z in vista.zonas if z.accion == 'seleccionar_item')
        antes = firma(app)
        clic(vista, item)
        assert firma(app) == antes and vista.item == item.argumento
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
        clic(vista, puerta)
        assert app.estado_partida().sala_actual_id == 2
        assert 'rata' in vista.atacantes
        assert vista.cambio_vida < 0
        assert vista.pausa_visual == 0.65
        antes_orientacion = firma(app)
        escena = vista.escena
        jugador_x = escena.posicion_jugador(vista)[0]
        for x, izquierda in [[jugador_x - 100, False], [jugador_x + 100, True]]:
            with patch.object(escena, 'posicion', return_value=[x, 200]), \
                 patch.object(escena.recursos, 'enemigo', wraps=escena.recursos.enemigo) as elegir, \
                 patch.object(escena, 'personaje', wraps=escena.personaje) as dibujar:
                escena.enemigos(vista, app.estado_partida(), 0)
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
            clic(vista, enemigo)
        assert vista.enemigo == 'rata'
        assert firma(app) == antes
        with patch('cripta.vista.grafica.ventana.monotonic', return_value=2):
            clic(vista, enemigo)                                  # lejos del anterior: no ataca
        assert firma(app) == antes
        with patch('cripta.vista.grafica.ventana.monotonic', return_value=2.2):
            clic(vista, enemigo)                                  # doble clic: ataca
        assert app.estado_partida().acciones_ejecutadas == 6
        assert vista.ultimo_click is None
        despues = firma(app)
        clic(vista, enemigo)                                      # durante la animación no actúa
        assert firma(app) == despues
        assert vista.accion_visual == 'atacar' and vista.pausa_visual == 0.65
        assert any(cambio < 0 for id_, cambio in vista.cambios_enemigos)
        vista.on_update(0.4)
        with patch.object(recursos, 'enemigo', wraps=recursos.enemigo) as elegir:
            vista.on_draw()
            assert any(c.kwargs.get('estado') == 'herido' for c in elegir.call_args_list)
        vista.on_update(1)
        vista.ejecutar('seleccionar_item', 'sala-1-objeto-8')
        vista.on_key_press(arcade.key.U, 0)
        assert app.inventario().buscar_por_id('sala-1-objeto-8') is None
        assert vista.cambio_vida > 0
        assert firma(reproducir(app._partida.registro.ruta, [FuenteReplay()])) == firma(app)
        antes_muerte = firma(app)
        vista.enemigos_muertos = [SimpleNamespace(id='caido', tipo='orco', nombre='Orco caído')]
        vista.pausa_visual = vista.duracion_visual = 1.2
        with patch.object(vista.escena, 'posicion', return_value=[300, 230]), \
             patch.object(recursos, 'enemigo', wraps=recursos.enemigo) as elegir:
            vista.on_draw()
            assert any(c.kwargs.get('estado') == 'muerto' for c in elegir.call_args_list)
            assert not any(z.accion == 'seleccionar' and z.argumento == 'caido' for z in vista.zonas)
            vista.on_update(1.3)
            elegir.reset_mock()
            vista.on_draw()
            assert not any(c.kwargs.get('estado') == 'muerto' for c in elegir.call_args_list)
        assert firma(app) == antes_muerte
        vista.enemigos_muertos = []
        for ancho, alto in [[640, 360], [1100, 740], [1366, 705], [1920, 1080]]:
            vista.set_size(ancho, alto)
            vista.on_draw()
            zonas_dentro(vista)
        antes = firma(app)
        vista.on_key_press(arcade.key.ESCAPE, 0)
        assert isinstance(vista.current_view, Panel)
        vista.current_view.on_key_press(arcade.key.ESCAPE, 0)
        assert vista.current_view is None and firma(app) == antes
        vista.on_key_press(arcade.key.ESCAPE, 0)
        vista.current_view.on_draw()
        terminar = next(z for z in vista.lienzo.zonas if z.accion == 'elegir'
                        and vista.current_view.opciones[int(z.argumento)][0] == 'Terminar la partida')
        clic(vista, terminar, vista.current_view)
        vista.current_view.on_draw()
        confirmar = next(z for z in vista.lienzo.zonas if z.accion == 'elegir')
        clic(vista, confirmar, vista.current_view)
        assert app.estado_partida().terminada
    finally:
        vista.close()
''')

    def test_grafica_en_red_usa_adaptador_existente(self):
        from unittest.mock import patch
        from cripta.bootstrap import main
        for argumentos in [[], ["--grafica"]]:   # Arcade es la vista por defecto; --grafica sigue aceptado
            with patch('cripta.bootstrap.NetworkAdapter') as red, \
                    patch('cripta.bootstrap.AlmacenDisco'), \
                    patch('cripta.vista.grafica.iniciar', return_value=0) as iniciar:
                self.assertEqual(main(argumentos), 0)
                red.assert_called_once()
                self.assertFalse(iniciar.call_args.args[-1])
