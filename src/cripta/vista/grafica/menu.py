"""Selección de cripta y datos de partida, sin iniciar la simulación al navegar."""
import arcade
from arcade.gui import UIManager, UIInputText

from .escena import ORO, TEXTO, FONDO


class InterfazMenu(UIManager):
    """Combina los botones dibujados con los campos de texto nativos."""

    def __init__(self, menu):
        """Conecta el gestor de widgets con la pantalla de selección."""
        super().__init__(window=menu.window)
        self.menu = menu

    def on_mouse_press(self, x, y, button, modifiers):
        """Prioriza los botones del menú y delega los demás clics a los campos."""
        if self.menu.on_mouse_press(x, y, button, modifiers):
            return True
        return super().on_mouse_press(x, y, button, modifiers)


class MenuPrincipal(arcade.View):
    """Selecciona la cripta y los datos del jugador antes de iniciar."""

    def __init__(self, ventana, cripta_id="", nombre="Jugador", semilla=""):
        """Prepara los campos del menú sin realizar consultas de red.

        Args:
            ventana: Ventana que comparte controlador y recursos gráficos.
            cripta_id: Identificador de la cripta preseleccionada.
            nombre: Nombre inicial para el campo del jugador.
            semilla: Texto inicial; vacío permite una semilla aleatoria.
        """
        super().__init__(ventana)
        self.controlador = ventana.controlador
        self.escena = ventana.escena
        self.criptas = []
        self.cripta_id = cripta_id
        self.seleccion = 0
        self.inicio_lista = 0
        self.detalles = None
        self.error = ""
        self.ui = InterfazMenu(self)
        self.nombre = self.ui.add(UIInputText(y=60, text=nombre, width=250, font_size=14))
        self.semilla = self.ui.add(UIInputText(y=20, text=semilla, width=250, font_size=14))

    def cargar(self):
        """Consulta la lista y los detalles iniciales desde la pantalla de carga."""
        self.criptas = self.controlador.listar_criptas()
        self.seleccion = next((i for i, c in enumerate(self.criptas) if c.id == self.cripta_id), 0)
        if self.criptas:
            self.detalles = self.controlador.previsualizar_cripta(self.criptas[self.seleccion].id)
        else:
            self.error = "No hay criptas disponibles."

    def on_show_view(self):
        """Activa los campos nativos al mostrar el menú."""
        self.ui.enable()

    def on_hide_view(self):
        """Desactiva los campos para que no reciban eventos de otras pantallas."""
        self.ui.disable()

    def elegir(self, indice, iniciar=False):
        """Carga los detalles de la selección antes de mostrarla o iniciar.

        Args:
            indice: Posición de la cripta en la lista disponible.
            iniciar: Si es True, inicia al recibir los detalles.
        """
        if not self.criptas:
            self.error = "No hay criptas disponibles."
            return
        self.seleccion = max(0, min(len(self.criptas) - 1, indice))
        def terminado(detalles):
            """Aplica los detalles consultados desde el hilo gráfico."""
            self.detalles = detalles
            self.error = ""
            if iniciar:
                self.comenzar()
            else:
                self.window.show_view(self)
        self.window.cargar("Leyendo cripta", lambda: self.controlador.previsualizar_cripta(self.criptas[self.seleccion].id), terminado)

    def on_draw(self):
        """Dibuja la lista, la vista previa y los campos según el tamaño actual."""
        self.clear(FONDO)
        e = self.escena
        e.zonas = []
        e.texto_actual = 0
        ancho, alto = [self.window.width, self.window.height]
        sx = ancho * 0.54
        campo_ancho = ancho - sx - 30
        e.texto("CRIPTA", 30, alto - 65, 32, ORO)
        e.texto(self.window.modo, ancho - 100, alto - 30, 10, ORO)
        e.texto("Elige tu próxima incursión", 30, alto - 95, 14)
        for i, cripta in enumerate(self.criptas[self.inicio_lista:self.inicio_lista + 6]):
            indice = self.inicio_lista + i
            e.boton(30, alto - 155 - i * 42, sx - 60, 34, cripta.nombre[:30], "cripta", str(indice),
                    ORO if indice == self.seleccion else TEXTO)
        if self.detalles:
            d = self.detalles
            e.texto(f"Vida {d.jugador_vida_max} · Inventario {d.inventario_max}", sx, alto - 140, 12)
            e.texto(f"Inicio: sala {d.sala_inicial} · Salida: {d.sala_salida}", sx, alto - 165, 12)
            e.texto(f"Presupuesto de red: {d.presupuesto_solicitudes}", sx, alto - 185, 11)
        for campo, etiqueta, y in [[self.nombre, "Nombre", alto - 250],
                                  [self.semilla, "Semilla (vacía = aleatoria)", alto - 330]]:
            e.texto(etiqueta, sx, y + 35, 12, ORO)
            campo.rect = arcade.LBWH(sx, y, campo_ancho, 30)
        e.texto(self.error[:max(20, int((ancho - 60) / 8))], 30, 100, 12)
        e.boton(sx, 40, campo_ancho, 42, "INICIAR PARTIDA", "iniciar")
        e.boton(30, 40, 150, 42, "SALIR", "salir")
        self.ui.draw()

    def comenzar(self):
        """Solicita el inicio usando el nombre, semilla y cripta elegidos."""
        if not self.criptas or self.detalles is None:
            return
        self.window.iniciar_partida(self.nombre.text, self.semilla.text, self.criptas[self.seleccion].id, self)

    def on_mouse_motion(self, x, y, dx, dy):
        """Actualiza la posición usada para resaltar botones."""
        self.escena.raton = [x, y]

    def on_mouse_press(self, x, y, button, modifiers):
        """Ejecuta el botón pulsado y devuelve True si consumió el clic."""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        for zona in self.escena.zonas:
            if zona.contiene(x, y):
                if zona.accion == "cripta":
                    self.elegir(int(zona.argumento), iniciar=True)
                elif zona.accion == "iniciar":
                    self.comenzar()
                elif zona.accion == "salir":
                    self.window.on_close()
                return True

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Recorre las criptas cuando el cursor está sobre su lista."""
        if x < self.window.width * 0.54:
            self.inicio_lista = max(0, min(max(0, len(self.criptas) - 6), self.inicio_lista - int(scroll_y)))
