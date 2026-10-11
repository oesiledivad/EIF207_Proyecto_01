"""Dibujo de la sala, HUD y zonas clickeables; sin reglas de juego."""
from dataclasses import dataclass
import math
import random
import textwrap

import arcade
from .distribucion import Distribucion


FONDO = [23, 21, 25]
TEXTO = [226, 214, 180]
ORO = [208, 164, 76]
ROJO = [184, 55, 49]


def lineas_bitacora(mensajes, ancho):
    """Ajusta mensajes al ancho indicado sin descartar líneas de su contenido.

    Args:
        mensajes: Textos que se mostrarán en orden.
        ancho: Límite de caracteres por línea.

    Returns:
        list: Líneas listas para dibujar o desplazar.
    """
    return [linea for mensaje in mensajes for linea in textwrap.wrap(mensaje, ancho) or [""]]

@dataclass
class Zona:
    """Define un rectángulo clickeable y la acción asociada, sin ejecutarla."""
    x: float
    y: float
    ancho: float
    alto: float
    accion: str
    argumento: str = ""

    def contiene(self, x, y):
        """Indica si el punto pertenece al rectángulo, incluidos sus bordes."""
        return self.x <= x <= self.x + self.ancho and self.y <= y <= self.y + self.alto


class Escena:
    """Dibuja los datos de la partida y produce zonas de interacción."""

    def __init__(self, recursos):
        """Conserva recursos compartidos, posiciones visuales y textos reutilizables."""
        self.recursos = recursos
        self.zonas = []
        self.textos = []
        self.texto_actual = 0
        self.distribucion = Distribucion()
        self.raton = [-1, -1]
        self.accion_activa = ""

    def texto(self, texto, x, y, tamano=12, color=TEXTO):
        """Reutiliza etiquetas de Arcade y actualiza únicamente propiedades cambiadas."""
        if self.texto_actual == len(self.textos):
            self.textos.append(arcade.Text(str(texto), x, y, color, tamano, font_name="Consolas"))
        etiqueta = self.textos[self.texto_actual]
        for atributo, valor in [["text", str(texto)], ["x", x], ["y", y],
                                ["font_size", tamano], ["color", color]]:
            actual = getattr(etiqueta, atributo)
            if atributo == "color":
                actual = list(actual)[:len(color)]
            if actual != valor:
                setattr(etiqueta, atributo, valor)
        etiqueta.draw()
        self.texto_actual += 1

    @staticmethod
    def bloque(x, y, ancho, alto, color):
        """Dibuja un rectángulo desde su esquina inferior izquierda."""
        arcade.draw_lbwh_rectangle_filled(x, y, ancho, alto, color)

    @staticmethod
    def sprite(textura, x, y, ancho, alto):
        """Dibuja una textura con escalado de píxeles sin suavizado."""
        arcade.draw_texture_rect(textura, arcade.LBWH(x, y, ancho, alto), pixelated=True)

    def boton(self, x, y, ancho, alto, etiqueta, accion, argumento="", color=ORO, icono=None):
        """Dibuja un botón y registra su zona para que la ventana gestione el clic."""
        zona = Zona(x, y, ancho, alto, accion, argumento)
        resaltado = zona.contiene(*self.raton) or accion == self.accion_activa
        self.bloque(x, y, ancho, alto, color if resaltado else [77, 72, 63])
        self.bloque(x + 2, y + 2, ancho - 4, alto - 4, [66, 54, 39] if resaltado else [35, 32, 32])
        margen = 8
        if icono:
            escala = (alto - 12) / max(icono.width, icono.height)
            self.sprite(icono, x + 8, y + 6, icono.width * escala, icono.height * escala)
            margen = 34
        self.texto(etiqueta, x + margen, y + alto / 2 - 5, 10, color)
        self.zonas.append(zona)

    def sala(self, p, rx, ry, rw, rh, cuadro):
        """Compone el suelo, paredes, iluminación y puertas del área de juego."""
        tile = min(48, rw / 12, rh / 8)
        self.suelo(p, rx, ry, rw, rh, tile)
        self.paredes(rx, ry, rw, rh, tile)
        self.sprite(self.recursos.antorchas[cuadro % 4], rx + tile, ry + rh - tile * 1.3, tile, tile)
        self.sprite(self.recursos.antorchas[(cuadro + 1) % 4], rx + rw - tile * 2, ry + rh - tile * 1.3, tile, tile)
        self.puertas(p, rx, ry, rw, rh, tile)

    def suelo(self, p, rx, ry, rw, rh, tile):
        """Dibuja variaciones del suelo reproducibles para cada sala y semilla."""
        azar = random.Random(f"suelo:{p.cripta_id}:{p.semilla}:{p.sala_actual_id}")
        for fila in range(math.ceil(rh / tile)):
            for col in range(math.ceil(rw / tile)):
                indice = 0 if azar.random() < 0.65 else azar.randrange(len(self.recursos.suelos))
                self.sprite(self.recursos.suelos[indice], rx + col * tile, ry + fila * tile,
                            min(tile, rw - col * tile), min(tile, rh - fila * tile))

    def paredes(self, rx, ry, rw, rh, tile):
        """Rodea el área de juego con paredes y esquinas del tileset."""
        for col in range(math.ceil(rw / tile)):
            x = rx + col * tile
            ancho = min(tile, rw - col * tile)
            self.sprite(self.recursos.pared, x, ry + rh - tile, ancho, tile)
            self.sprite(self.recursos.borde, x, ry, ancho, tile / 2)
            self.sprite(self.recursos.borde, x, ry + rh - tile / 2, ancho, tile / 2)
        for fila in range(math.ceil(rh / tile)):
            y = ry + fila * tile
            alto = min(tile, rh - fila * tile)
            self.sprite(self.recursos.pared_izquierda, rx, y, tile / 2, alto)
            self.sprite(self.recursos.pared_derecha, rx + rw - tile / 2, y, tile / 2, alto)
        for y in [ry, ry + rh - tile / 2]:
            self.sprite(self.recursos.esquina_izquierda, rx, y, tile / 2, tile / 2)
            self.sprite(self.recursos.esquina_derecha, rx + rw - tile / 2, y, tile / 2, tile / 2)

    def puertas(self, p, rx, ry, rw, rh, tile):
        """Ubica las salidas de la sala en los cuatro extremos del área."""
        for salida in p.vecindad:
            ancho, alto = [tile * 1.5, tile * 1.5]
            x, y = [rx + (rw - ancho) / 2, ry + rh - alto]
            if salida.direccion == "S":
                y = ry
            elif salida.direccion == "O":
                x, y = [rx, ry + (rh - alto) / 2]
            elif salida.direccion == "E":
                x, y = [rx + rw - ancho, ry + (rh - alto) / 2]
            self.entrada(salida, x, y, ancho, alto)
            self.texto(salida.direccion + (" [llave]" if salida.cerrada else ""), x + 3, y + 4, 9, ORO)
            self.zonas.append(Zona(x, y, ancho, alto, "abrir" if salida.cerrada else "mover", salida.direccion))

    def entrada(self, salida, x, y, ancho, alto):
        """Dibuja una puerta orientada y registra la acción de abrir o mover."""
        self.sprite(self.recursos.suelos[0], x, y, ancho, alto)
        cuadros = next(c for d, c in self.recursos.puertas if d == salida.direccion)
        textura = cuadros[1 if salida.cerrada else 0]
        escala = min(ancho / textura.width, alto / textura.height)
        w, h = [textura.width * escala, textura.height * escala]
        self.sprite(textura, x + (ancho - w) / 2, y, w, h)

    def dibujar(self, vista, p, inventario, mensajes):
        """Compone un cuadro completo y renueva sus zonas de interacción.

        Args:
            vista: Ventana con selecciones, animaciones y tamaño actuales.
            p: Estado de la partida, usado solo para consultar datos.
            inventario: Inventario que se presenta sin alterar su orden real.
            mensajes: Textos visibles de la bitácora.
        """
        self.zonas = []
        self.texto_actual = 0
        self.raton = vista.raton
        self.accion_activa = vista.accion_visual if vista.pausa_visual else ""
        ancho = vista.width
        alto = vista.height
        lateral = max(185, ancho * 0.23)
        rx, ry = [20, 155]
        rw, rh = [ancho - lateral - 45, alto - 215]
        self.distribucion.preparar(p)
        self.texto(f"CRIPTA · {p.sala_actual_nombre}", 20, alto - 32, 16, ORO)
        self.bloque(rx, ry, rw, rh, [48, 45, 36])
        cuadro = int(vista.animacion * 6)
        self.sala(p, rx, ry, rw, rh, cuadro)
        self.jugador(vista, p, rx, ry, rw, rh, cuadro)
        self.enemigos(vista, p, rx, ry, rw, rh, cuadro)
        self.objetos(vista, p, rx, ry, rw, rh)
        sx = ancho - lateral
        self.inventario(vista, inventario, sx, lateral, alto)
        self.bitacora(vista, mensajes, sx, lateral, alto)
        self.hud(vista, p, ancho)
        self.minimapa(p, ancho - 138, 12)

    def minimapa(self, p, x, y):
        """Dibuja la sala actual y sus vecinas en un mapa local clickeable."""
        anteriores = self.zonas
        self.zonas = []
        self.bloque(x - 4, y - 4, 122, 118, [15, 14, 19, 225])
        self.texto("MAPA · X salida", x, y + 100, 9, ORO)
        self.bloque(x + 40, y + 32, 34, 30, ORO)
        self.texto(str(p.sala_actual_id), x + 46, y + 42, 11, FONDO)
        for vecina in p.vecindad:
            for direccion, dx, dy in [["N", 40, 64], ["S", 40, 0], ["O", 0, 32], ["E", 80, 32]]:
                if vecina.direccion == direccion:
                    color = ROJO if vecina.cerrada else ORO if vecina.es_salida_final else TEXTO
                    self.boton(x + dx, y + dy, 34, 30, str(vecina.sala_id), "mover_mapa", direccion, color)
                    if vecina.cerrada or vecina.es_salida_final:
                        self.texto("K" if vecina.cerrada else "X", x + dx + 24, y + dy + 20, 8, color)
        self.zonas += anteriores

    def jugador(self, vista, p, rx, ry, rw, rh, cuadro):
        """Dibuja al jugador orientado al objetivo, con su animación actual."""
        px, py = [rx + rw * 0.34, ry + rh * 0.45]
        if vista.pausa_visual and vista.accion_visual == "mover":
            px -= vista.pausa_visual * 120
        objetivo = next((pos for pos in self.distribucion.posiciones
                         if pos[:3] == [p.sala_actual_id, "enemigo", vista.enemigo]), None)
        izquierda = objetivo is not None and self.distribucion.posicion(p.sala_actual_id, "enemigo", vista.enemigo, rx, ry, rw, rh)[0] < px
        accion = 0
        transcurrido = max(0, vista.duracion_visual - vista.pausa_visual)
        progreso = transcurrido / 0.65
        herido = vista.pausa_visual > 0 and (vista.cambio_vida < 0 or bool(vista.atacantes))
        if vista.pausa_visual and vista.accion_visual == "mover":
            accion = 1
        elif vista.pausa_visual and vista.accion_visual == "atacar":
            accion = 2
        if p.derrota:
            accion = 4
            progreso = transcurrido / vista.duracion_visual
        elif herido:
            # Si atacó y recibió daño, se muestra primero el ataque y después el golpe.
            if accion == 2 and transcurrido < 0.325:
                progreso = transcurrido / 0.325
            else:
                progreso = (transcurrido - 0.325) / 0.325 if accion == 2 else transcurrido / 0.65
                accion = 3
        animacion = (self.recursos.soldado_izquierda if izquierda else
                     [self.recursos.soldado_idle, self.recursos.soldado_correr, self.recursos.soldado_atacar,
                      self.recursos.soldado_herido, self.recursos.soldado_morir])[accion]
        indice = cuadro % len(animacion)
        if accion in [2, 3, 4]:
            indice = min(len(animacion) - 1, int(progreso * len(animacion)))
        textura = animacion[indice]
        ancho_jugador = min(64, rw * 0.10, rh * 0.13)
        referencia = self.recursos.soldado_idle[0]
        alto_jugador = self.personaje(textura, referencia, px, py, ancho_jugador, rh * 0.24, izquierda=izquierda)
        if vista.pausa_visual and vista.cambio_vida:
            self.numero(vista.cambio_vida, px, py + alto_jugador, vista.pausa_visual, vista.duracion_visual)

    def personaje(self, textura, referencia, x, y, ancho, alto, izquierda=False):
        """Mantiene el tamaño del cuerpo y la posición de los pies entre animaciones.

        Args:
            textura: Cuadro que se va a dibujar.
            referencia: Cuadro idle usado para calcular el tamaño del cuerpo.
            x: Posición horizontal del cuerpo visible.
            y: Altura de los pies.
            ancho: Anchura máxima del cuerpo de referencia.
            alto: Altura máxima del cuerpo de referencia.
            izquierda: Ajusta el margen para una textura reflejada por la GPU.

        Returns:
            float: Altura del cuerpo de referencia escalado.
        """
        # Los márgenes transparentes y el arma no deben encoger el cuerpo al atacar.
        caja = referencia.image.getbbox() or [0, 0, referencia.width, referencia.height]
        if izquierda:
            caja = [referencia.width - caja[2], caja[1], referencia.width - caja[0], caja[3]]
        escala = min(ancho / (caja[2] - caja[0]), alto / (caja[3] - caja[1]))
        self.sprite(textura, x - caja[0] * escala, y - (referencia.height - caja[3]) * escala,
                    textura.width * escala, textura.height * escala)
        return (caja[3] - caja[1]) * escala

    def numero(self, valor, x, y, pausa, duracion=0.65):
        """Dibuja un cambio de vida flotante con signo y color de daño o curación."""
        y += 12 + (duracion - pausa) * 35
        texto = f"{valor:+}"
        self.texto(texto, x + 2, y - 2, 30, [12, 11, 14])
        self.texto(texto, x, y, 30, [96, 235, 125] if valor > 0 else [255, 85, 75])

    def enemigos(self, vista, p, rx, ry, rw, rh, cuadro):
        """Dibuja enemigos orientados al jugador y conserva temporalmente sus muertes."""
        celda_alto = rh * 0.56 / self.distribucion.filas(p.sala_actual_id)
        tamano_enemigo = min(80, rw * 0.115, celda_alto - 10)
        jugador_x = rx + rw * 0.34 - (vista.pausa_visual * 120 if vista.accion_visual == "mover" else 0)
        transcurrido = max(0, vista.duracion_visual - vista.pausa_visual)
        for enemigo in p.enemigos + (vista.enemigos_muertos if vista.pausa_visual else []):
            x, y = self.distribucion.posicion(p.sala_actual_id, "enemigo", enemigo.id, rx, ry, rw, rh)
            tamano = max(4, tamano_enemigo)
            atacando = vista.pausa_visual > 0 and enemigo.id in vista.atacantes
            muerto = enemigo in vista.enemigos_muertos
            herido = vista.pausa_visual > 0 and any(id_ == enemigo.id and cambio < 0 for id_, cambio in vista.cambios_enemigos)
            estado = "muerto" if muerto else "herido" if herido and (not atacando or transcurrido >= 0.325) else ""
            izquierda = x > jugador_x
            cuadros = self.recursos.enemigo(enemigo, atacar=atacando, izquierda=izquierda, estado=estado)
            progreso = transcurrido / 0.65
            if muerto:
                progreso = transcurrido / vista.duracion_visual
            elif herido and atacando:
                progreso = (transcurrido - 0.325) / 0.325 if estado else transcurrido / 0.325
            indice = min(len(cuadros) - 1, int(max(0, progreso) * len(cuadros))) if atacando or estado else cuadro % len(cuadros)
            textura = cuadros[indice]
            altura = self.personaje(textura, self.recursos.enemigo(enemigo)[0], x, y, tamano, tamano, izquierda=izquierda)
            anchura = tamano
            if muerto:
                continue
            if atacando:
                self.bloque(x, y - 3, anchura, 3, ROJO)
            self.bloque(x, y + tamano + 3, tamano, 3, [38, 27, 26])
            self.bloque(x, y + tamano + 3, tamano * enemigo.vida / max(1, enemigo.vida_max), 3, ROJO)
            if enemigo.id == vista.enemigo:
                self.bloque(x, y - 4, tamano, 2, ORO)
            if Zona(x, y, tamano, tamano + 6, "seleccionar").contiene(*vista.raton):
                self.texto(enemigo.nombre[:max(3, int(rw * 0.12 / 5))], x, y - 10, 8)
            self.zonas.append(Zona(x, y, tamano, tamano + 6, "seleccionar", enemigo.id))
        if vista.pausa_visual:
            for id_, cambio in vista.cambios_enemigos:
                if cambio:
                    x, y = self.distribucion.posicion(p.sala_actual_id, "enemigo", id_, rx, ry, rw, rh)
                    self.numero(cambio, x, y + max(4, tamano_enemigo), vista.pausa_visual, vista.duracion_visual)

    def objetos(self, vista, p, rx, ry, rw, rh):
        """Dibuja objetos flotantes conservando una zona de recogida estable."""
        celda_alto = rh * 0.56 / self.distribucion.filas(p.sala_actual_id)
        tamano = max(8, min(40, rw * 0.10, celda_alto - 14))
        for i, objeto in enumerate(p.objetos_suelo):
            x, y = self.distribucion.posicion(p.sala_actual_id, "objeto", objeto.id, rx, ry, rw, rh)
            flotacion = 5 + math.sin(vista.animacion * 3 + i) * 3
            arcade.draw_ellipse_filled(x + tamano / 2, y + 2, tamano * 0.8, 6, [12, 11, 14, 170])
            arcade.draw_ellipse_outline(x + tamano / 2, y + 3, tamano * 0.9, 8, [208, 164, 76, 130], 1)
            icono = self.recursos.icono(objeto)
            escala = tamano / max(icono.width, icono.height)
            ancho, alto = [icono.width * escala, icono.height * escala]
            self.sprite(icono, x + (tamano - ancho) / 2, y + flotacion, ancho, alto)
            zona = Zona(x, y, tamano, tamano + 8, "recoger", objeto.id)
            if zona.contiene(*vista.raton):
                self.texto(objeto.nombre[:max(3, int(rw * 0.12 / 5))], x, y - 10, 8, ORO)
            self.zonas.append(zona)

    def inventario(self, vista, inventario, sx, lateral, alto):
        """Distribuye todas las casillas y muestra el orden visual seleccionado."""
        self.texto("INVENTARIO", sx, alto - 70, 15, ORO)
        self.boton(sx, alto - 98, lateral - 14, 22,
                   f"{inventario.tamano}/{inventario.capacidad} · {getattr(vista, 'criterio', 'real')}", "ordenar")
        criterio = getattr(vista, "criterio", "real")
        items = getattr(inventario, f"vista_por_{criterio}")() if criterio != "real" else inventario.items()
        columnas = min(4, max(1, inventario.capacidad))
        filas = max(1, math.ceil(inventario.capacidad / columnas))
        tamano = min(42, (lateral - 14) / columnas - 6, 94 / filas - 6)
        for i in range(inventario.capacidad):
            x, y = [sx + (i % columnas) * (tamano + 6), alto - 110 - tamano - (i // columnas) * (tamano + 6)]
            self.bloque(x - 2, y - 2, tamano + 4, tamano + 4, [77, 72, 63])
            self.bloque(x, y, tamano, tamano, [35, 32, 32])
            if i < len(items):
                self.casilla(items[i], vista.item, x, y, tamano)
        seleccionado = inventario.buscar_por_id(vista.item)
        self.texto(seleccionado.nombre[:int(lateral / 6)] if seleccionado else "Selecciona un objeto", sx, alto - 215, 10)
        for i, accion in enumerate(["usar", "equipar", "soltar"]):
            self.boton(sx + i * (lateral - 14) / 3, alto - 248, (lateral - 14) / 3 - 3, 25, accion.upper(), accion)

    def casilla(self, item, seleccionado, x, y, tamano):
        """Dibuja un objeto, sus marcas de selección y equipo, y registra el clic."""
        if item.instancia_id == seleccionado:
            self.bloque(x - 2, y - 2, tamano + 4, tamano + 4, ORO)
            self.bloque(x, y, tamano, tamano, [44, 38, 34])
        icono = self.recursos.icono(item)
        escala = max(1, tamano - 6) / max(icono.width, icono.height)
        ancho, alto = [icono.width * escala, icono.height * escala]
        self.sprite(icono, x + (tamano - ancho) / 2, y + (tamano - alto) / 2, ancho, alto)
        if item.equipado:
            self.texto("E", x + 3, y + 3, 9, ORO)
        self.zonas.append(Zona(x, y, tamano, tamano, "seleccionar_item", item.instancia_id))

    def bitacora(self, vista, mensajes, sx, lateral, alto):
        """Dibuja las líneas visibles y calcula los límites del historial."""
        self.texto("BITÁCORA", sx, alto - 265, 15, ORO)
        cantidad = max(1, int((alto - 450) / 16) + 1)
        lineas = lineas_bitacora(mensajes, max(15, int((lateral - 14) / 8)))
        vista.bitacora_limite = max(0, len(lineas) - cantidad)
        vista.bitacora_desplazamiento = min(vista.bitacora_desplazamiento, vista.bitacora_limite)
        fin = len(lineas) - vista.bitacora_desplazamiento
        for i, texto in enumerate(lineas[max(0, fin - cantidad):fin]):
            self.texto(texto, sx, alto - 290 - i * 16, 10)
        self.texto("Rueda: historial", sx, 145, 10)

    def hud(self, vista, p, ancho):
        """Dibuja vida, efectos, mensajes y controles debajo de la cripta."""
        self.texto("♥", 20, 101, 28, ROJO)
        self.texto(f"VIDA {p.jugador_vida}/{p.jugador_vida_max}  ·  t={p.reloj_virtual}", 62, 119, 14)
        self.texto(" | ".join(p.efectos)[:max(1, int((ancho - 485) / 8))], 330, 119, 10, ORO)
        self.bloque(62, 101, 180, 12, [51, 35, 33])
        self.bloque(62, 101, 180 * p.jugador_vida / max(1, p.jugador_vida_max), 12, ROJO)
        self.texto(vista.mensaje[:max(20, int((ancho - 175) / 9))], 20, 80, 11)
        acciones = [["ATACAR [A]", "atacar"], ["ESPERAR [.]", "esperar"],
                    ["PERGAMINO [P]", "retroceder"], ["AYUDA [?]", "ayuda"],
                    ["TERMINAR [Q]", "terminar"], ["SALA [I]", "informacion"]]
        for i, accion in enumerate(acciones):
            celda = (ancho - 175) / 3
            self.boton(20 + i % 3 * celda, 45 - i // 3 * 32, celda - 6, 28, accion[0], accion[1])



