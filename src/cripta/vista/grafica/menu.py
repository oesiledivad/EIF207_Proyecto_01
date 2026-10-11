"""Selección de cripta y datos de partida, sin iniciar la simulación al navegar."""

import arcade

from . import fuente_pixel as fp
from .lienzo import ALTO, ANCHO, ORO, ROJO, TEXTO, TEXTO_SUAVE


class CampoTexto:
    """Campo de texto propio dibujado en el lienzo (escala igual que todo lo demás)."""

    def __init__(self, texto="", largo_max=24, solo_digitos=False):
        self.text = texto
        self.largo_max = largo_max
        self.solo_digitos = solo_digitos

    def escribir(self, caracteres):
        for c in caracteres:
            if c.isprintable() and len(self.text) < self.largo_max and (c.isdigit() or not self.solo_digitos):
                self.text += c

    def borrar(self):
        self.text = self.text[:-1]


class MenuPrincipal(arcade.View):
    """Selecciona la cripta y los datos del jugador antes de iniciar."""

    VISIBLES = 7

    def __init__(self, ventana, cripta_id="", nombre="Jugador", semilla=""):
        """Prepara los campos del menú sin realizar consultas de red."""
        super().__init__(ventana)
        self.controlador = ventana.controlador
        self.escena = ventana.escena
        self.criptas = []
        self.cripta_id = cripta_id
        self.seleccion = 0
        self.inicio_lista = 0
        self.detalles = None
        self.error = ""
        self.tiempo = 0.0
        self.nombre = CampoTexto(nombre)
        self.semilla = CampoTexto(semilla, 10, solo_digitos=True)
        self.foco = self.nombre

    def cargar(self):
        """Consulta la lista y los detalles iniciales desde la pantalla de carga."""
        self.criptas = self.controlador.listar_criptas()
        self.seleccion = next((i for i, c in enumerate(self.criptas) if c.id == self.cripta_id), 0)
        if self.criptas:
            self.detalles = self.controlador.previsualizar_cripta(self.criptas[self.seleccion].id)
        else:
            self.error = "No hay criptas disponibles."

    def elegir(self, indice, iniciar=False):
        """Carga los detalles de la selección antes de mostrarla o iniciar."""
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

    def on_update(self, delta_time):
        self.tiempo += delta_time

    def on_draw(self):
        """Lista de criptas a la izquierda; datos y campos a la derecha."""
        v = self.window
        l = v.lienzo
        l.iniciar(v)
        r = self.escena.recursos
        cuadro = int(self.tiempo * 6)
        for i, x in enumerate([60, ANCHO - 60]):
            l.imagen(r.resplandores[(int(self.tiempo * 3) + i) % 3], x - 48, ALTO - 112, 96, 96)
            l.imagen(r.antorchas[(cuadro + i) % 4], x - 16, ALTO - 80, 32, 32)
        l.texto("CRIPTA", ANCHO / 2, ALTO - 74, 6, ORO, negrita=True, ancla="centro", sombra=True)
        l.texto("Elige tu próxima incursión", ANCHO / 2, ALTO - 96, 1, TEXTO_SUAVE, ancla="centro")
        l.texto(v.modo, ANCHO - 10, ALTO - 16, 1, TEXTO_SUAVE, ancla="derecha")

        # Lista de criptas
        x0, arriba = 40, ALTO - 120
        l.panel(x0 - 10, 70, 360, arriba - 60)
        l.texto("CRIPTAS", x0, arriba - 22, 2, (210, 200, 176), negrita=True)
        l.rect(x0, arriba - 28, 340, 2, (70, 64, 56))
        for i, cripta in enumerate(self.criptas[self.inicio_lista:self.inicio_lista + self.VISIBLES]):
            indice = self.inicio_lista + i
            elegido = indice == self.seleccion
            l.boton(x0, arriba - 64 - i * 32, 340, 28, fp.recortar(cripta.nombre, 300, 1, True), "cripta",
                    str(indice), activo=elegido, color=TEXTO,
                    ayuda=f"{cripta.id} · {cripta.salas} salas · dificultad {cripta.dificultad}")
        if len(self.criptas) > self.VISIBLES:
            l.texto("rueda: más criptas", x0 + 340, arriba - 22, 1, TEXTO_SUAVE, ancla="derecha")

        # Detalles y campos
        x1 = 430
        l.panel(x1 - 10, 70, ANCHO - x1 - 20, arriba - 60)
        if self.detalles:
            d = self.detalles
            nombre = self.criptas[self.seleccion].nombre if self.criptas else d.id
            l.texto(fp.recortar(nombre.upper(), 330, 2, True), x1, arriba - 22, 2, ORO, negrita=True)
            for i, linea in enumerate([f"{d.salas_total} salas · inicio en la sala {d.sala_inicial}",
                                       f"Vida {d.jugador_vida_max} · Ataque {d.jugador_ataque} · "
                                       f"Defensa {d.jugador_defensa}",
                                       f"Inventario {d.inventario_max} · Red: {d.presupuesto_solicitudes} solicitudes"]):
                l.texto(linea, x1, arriba - 42 - i * 13, 1, TEXTO)
        for i, (campo, etiqueta) in enumerate([[self.nombre, "NOMBRE"],
                                               [self.semilla, "SEMILLA (vacía = aleatoria)"]]):
            y = arriba - 128 - i * 52
            l.texto(etiqueta, x1, y + 30, 1, ORO, negrita=True)
            enfocado = campo is self.foco
            l.panel(x1, y, ANCHO - x1 - 40, 24, resaltado=enfocado, fondo=(14, 13, 16))
            cursor = "_" if enfocado and int(self.tiempo * 2) % 2 == 0 else ""
            l.texto(fp.recortar(campo.text, ANCHO - x1 - 60, 2) + cursor, x1 + 8, y + 7, 2, TEXTO)
            l.zona(x1, y, ANCHO - x1 - 40, 24, "foco", str(i), "Escribe aquí")
        if self.error:
            l.texto(fp.recortar(self.error, ANCHO - x1 - 30), x1, 112, 1, ROJO)
        l.boton(x1, 80, ANCHO - x1 - 40, 30, "INICIAR PARTIDA", "iniciar", tam=2, activo=bool(self.detalles),
                ayuda="Enter")
        l.boton(40, 26, 140, 30, "SALIR", "salir", tam=2)
        l.texto("Clic en una cripta para elegirla · Tab cambia de campo · Enter inicia · F11 pantalla completa",
                ANCHO / 2 + 90, 36, 1, TEXTO_SUAVE, ancla="centro")
        l.globo_ayuda()
        l.bandas(v)

    def comenzar(self):
        """Solicita el inicio usando el nombre, semilla y cripta elegidos."""
        if not self.criptas or self.detalles is None:
            return
        self.window.iniciar_partida(self.nombre.text, self.semilla.text, self.criptas[self.seleccion].id, self)

    def on_mouse_motion(self, x, y, dx, dy):
        """Actualiza la posición usada para resaltar botones."""
        self.window.raton = self.window.lienzo.a_virtual(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Ejecuta el botón pulsado y devuelve True si consumió el clic."""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return None
        vx, vy = self.window.lienzo.a_virtual(x, y)
        for zona in self.window.lienzo.zonas:
            if zona.contiene(vx, vy):
                if zona.accion == "cripta":
                    self.elegir(int(zona.argumento))
                elif zona.accion == "foco":
                    self.foco = [self.nombre, self.semilla][int(zona.argumento)]
                elif zona.accion == "iniciar":
                    self.comenzar()
                elif zona.accion == "salir":
                    self.window.on_close()
                return True
        return None

    def on_text(self, texto):
        """Escribe en el campo con foco (lo envía arcade/pyglet al teclear)."""
        self.foco.escribir(texto)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.BACKSPACE:
            self.foco.borrar()
        elif symbol == arcade.key.TAB:
            self.foco = self.semilla if self.foco is self.nombre else self.nombre
        elif symbol in (arcade.key.ENTER, arcade.key.RETURN):
            self.comenzar()
        elif symbol == arcade.key.UP:
            self.elegir(self.seleccion - 1)
        elif symbol == arcade.key.DOWN:
            self.elegir(self.seleccion + 1)
        else:
            return None
        return True

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Recorre las criptas cuando el cursor está sobre su lista."""
        vx, _ = self.window.lienzo.a_virtual(x, y)
        if vx < ANCHO / 2:
            self.inicio_lista = max(0, min(max(0, len(self.criptas) - self.VISIBLES),
                                           self.inicio_lista - int(scroll_y)))
