"""Dibujo de la sala, el HUD y las zonas clickeables; sin reglas de juego.

Todo está en coordenadas del lienzo virtual de 800x450 (ver lienzo.py):

    ┌ título ─────────────────────────────┐┌ INVENTARIO ┐
    │                                     ││            │
    │               SALA                  ││ BITÁCORA   │
    │                                     ││            │
    └─────────────────────────────────────┘└────────────┘
    ┌ ♥ vida ─┬ MOVER ─ ATACAR ─ ESPERAR ─ [⟲][🔍][⎋] ─┐
"""
import math
import random

from PIL import Image
from cripta.estructuras.Ordenamientos import ordenar

from . import fuente_pixel as fp
from . import pixelart as pa
from .distribucion import Distribucion
from .lienzo import ALTO, ANCHO, FONDO, ORO, ROJO, TEXTO, TEXTO_SUAVE, VERDE, Lienzo, Zona  # noqa: F401

# Sala (los muros son parte del rectángulo)
SALA_X, SALA_Y, SALA_ANCHO, SALA_ALTO = 12, 92, 576, 320
K = 2                       # cada píxel del arte ocupa 2x2 píxeles virtuales
T = 16 * K                  # baldosa
MURO_FONDO = 80             # muro del fondo (cara de ladrillo + borde superior)
MURO_LADO = 32
MURO_ABAJO = 24
SUELO_X = SALA_X + MURO_LADO
SUELO_Y = SALA_Y + MURO_ABAJO
SUELO_ANCHO = SALA_ANCHO - 2 * MURO_LADO
SUELO_ALTO = SALA_ALTO - MURO_ABAJO - MURO_FONDO

# Panel lateral y barra inferior
PANEL_X, PANEL_Y, PANEL_ANCHO, PANEL_ALTO = 600, 84, 192, 358
BARRA_X, BARRA_Y, BARRA_ANCHO, BARRA_ALTO = 8, 8, 784, 70

# Compatibilidad con pantallas que usan estos nombres
FONDO = FONDO


def lineas_bitacora(mensajes, ancho):
    """Ajusta mensajes a `ancho` píxeles virtuales sin perder contenido."""
    return [linea for mensaje in mensajes for linea in fp.envolver(mensaje, ancho) or [""]]


def arcade_textura(imagen):
    import arcade
    return arcade.Texture(imagen)


class Escena:
    """Dibuja los datos de la partida y produce zonas de interacción."""

    def __init__(self, recursos, lienzo=None):
        self.recursos = recursos
        self.lienzo = lienzo or Lienzo()
        self.distribucion = Distribucion()
        self.accion_activa = ""
        self._clave_sala = None
        self._textura_sala = None
        # Trampas: ids que ya se vieron disparadas y dardos en vuelo [x, y, inicio].
        self._clave_trampas = None
        self._disparadas: list[str] = []
        self._dardos: list[list] = []

    # Atajos usados por otras pantallas
    @property
    def zonas(self):
        return self.lienzo.zonas

    @zonas.setter
    def zonas(self, valor):
        self.lienzo.zonas = valor

    @property
    def raton(self):
        return self.lienzo.raton

    @raton.setter
    def raton(self, valor):
        self.lienzo.raton = valor

    def texto(self, *args, **kwargs):
        return self.lienzo.texto(*args, **kwargs)

    def boton(self, *args, **kwargs):
        return self.lienzo.boton(*args, **kwargs)

    #  Cuadro completo

    def dibujar(self, vista, p, inventario, mensajes, interactivo=True):
        """Compone un cuadro completo y renueva sus zonas de interacción.

        Args:
            vista: Ventana con selecciones, animaciones y tamaño actuales.
            p: Estado de la partida, usado solo para consultar datos.
            inventario: Inventario que se presenta sin alterar su orden real.
            mensajes: Textos visibles de la bitácora.
            interactivo: False para dibujarla de fondo (paneles, fin) sin zonas.
        """
        l = self.lienzo
        self.accion_activa = vista.accion_visual if vista.pausa_visual else ""
        self.distribucion.preparar(p)
        self._preparar_sala(p)
        cuadro = int(vista.animacion * 6)

        l.texto(f"CRIPTA — SALA {p.sala_actual_id}", SALA_X + 2, ALTO - 22, 2, (196, 186, 160), negrita=True)
        ancho_titulo = fp.ancho_texto(f"CRIPTA — SALA {p.sala_actual_id}", 2, True)
        l.texto(fp.recortar(f"· {p.sala_actual_nombre}", SALA_ANCHO - ancho_titulo - 150),
                SALA_X + 10 + ancho_titulo, ALTO - 22, 1, TEXTO_SUAVE)
        l.texto(f"t={p.reloj_virtual} · {vista.indicador_red()}", SALA_X + SALA_ANCHO, ALTO - 22, 1,
                TEXTO_SUAVE, ancla="derecha")

        self.sala(vista, p, cuadro)
        self.entidades(vista, p, cuadro)
        self.dardos_en_vuelo(vista)
        self.minimapa(vista, p)
        self.mensaje_estado(vista)
        self.inventario(vista, inventario)
        self.bitacora(vista, mensajes)
        self.hud(vista, p)
        if not interactivo:
            l.zonas = []
            l.ayuda = ""

    #  Sala

    def _preparar_sala(self, p):
        """Compone el fondo estático de la sala en UNA textura (una vez por sala).

        Suelo, muros, columnas y decoración no cambian mientras el jugador está en
        la sala, así que se arman con PIL y se dibujan con una sola llamada. El
        azar visual es propio (no toca el azar de la simulación).
        """
        clave = [p.cripta_id, p.semilla, p.sala_actual_id]
        if clave == self._clave_sala:
            return
        self._clave_sala = clave
        azar = random.Random(f"suelo:{p.cripta_id}:{p.semilla}:{p.sala_actual_id}")
        r = self.recursos
        lugares = [[SUELO_X + 18, SUELO_Y + 150], [SUELO_X + 22, SUELO_Y + 40],
                   [SUELO_X + 30, SUELO_Y + 196], [SUELO_X + SUELO_ANCHO - 26, SUELO_Y + 190],
                   [SUELO_X + SUELO_ANCHO - 30, SUELO_Y + 120], [SUELO_X + 110, SUELO_Y + 198],
                   [SUELO_X + SUELO_ANCHO - 120, SUELO_Y + 200], [SUELO_X + 16, SUELO_Y + 96]]
        suelo = [azar.randrange(len(r.img_baldosas)) if azar.random() < 0.55 else 9
                 for _ in range(7 * (SUELO_ANCHO // T))]
        azar.shuffle(lugares)
        decoracion = [[azar.randrange(len(r.img_decoracion)), x, y] for x, y in lugares[:azar.randint(3, 5)]]
        self._textura_sala = arcade_textura(self._componer_sala(suelo, decoracion))

    def _componer_sala(self, suelo, decoracion):
        """Imagen de 288x160 píxeles de arte (la sala completa sin puertas ni antorchas)."""
        r = self.recursos
        ancho, alto = SALA_ANCHO // K, SALA_ALTO // K              # 288 x 160
        img = Image.new("RGBA", [ancho, alto], (8, 8, 10, 255))
        lado, arriba_suelo, abajo_suelo = MURO_LADO // K, MURO_FONDO // K, alto - MURO_ABAJO // K
        columnas = SUELO_ANCHO // T
        for i, indice in enumerate(suelo):                          # suelo
            fila, col = divmod(i, columnas)
            pa.componer(img, r.img_baldosas[indice], lado + col * 16, arriba_suelo + fila * 16)
        for i, alfa in enumerate([110, 70, 40, 18]):                 # sombra del muro del fondo
            pa.sombra(img, [lado, arriba_suelo + i * 3, ancho - lado - 1, arriba_suelo + i * 3 + 2], alfa)
        for col in range(ancho // 16):                               # muro del fondo
            for fila in range(2):
                pa.componer(img, r.img_ladrillos[(col * 3 + fila) % 4], col * 16, 8 + fila * 16)
            pa.componer(img, r.img_borde[col % 4], col * 16, 0)
        for x in range(ancho):
            img.putpixel([x, 8], (40, 35, 27, 255))
        for centro in [38, 98, 190, 250]:                            # columnas
            pa.componer(img, r.img_pilar, centro - 6, 0)
        for i, y in enumerate(range(abajo_suelo - 16, -16, -16)):    # muros laterales
            pa.componer(img, r.img_muro[i % 4], 0, y)
            pa.componer(img, r.img_muro[(i + 2) % 4], ancho - lado, y)
        pa.sombra(img, [lado, arriba_suelo, lado, abajo_suelo - 1], 150)
        pa.sombra(img, [ancho - lado - 1, arriba_suelo, ancho - lado - 1, abajo_suelo - 1], 150)
        pa.sombra(img, [0, abajo_suelo, ancho - 1, alto - 1], 255)    # muro inferior
        for col in range(ancho // 16):
            pa.componer(img, r.img_borde[(col + 1) % 4], col * 16, abajo_suelo + 3)
        for x in range(lado, ancho - lado):
            img.putpixel([x, abajo_suelo], (150, 135, 100, 255))
        for indice, x, y in ordenar(decoracion.copy(), key=lambda d: -d[2]):  # atrás primero
            figura = r.img_decoracion[indice]
            ax, ay = int((x - SALA_X) / K), int(alto - (y - SALA_Y) / K)
            pa.sombra_ovalada(img, ax, ay, int(figura.width * 0.9), 3)
            pa.componer(img, figura, ax - figura.width // 2, ay - figura.height)
        for i, alfa in enumerate([70, 45, 25]):                      # viñeta
            pa.sombra(img, [lado + i * 3, arriba_suelo, lado + i * 3 + 2, abajo_suelo - 1], alfa)
            pa.sombra(img, [ancho - lado - 3 - i * 3, arriba_suelo, ancho - lado - 1 - i * 3, abajo_suelo - 1], alfa)
            pa.sombra(img, [lado, abajo_suelo - 3 - i * 3, ancho - lado - 1, abajo_suelo - 1 - i * 3], alfa)
        return img

    def sala(self, vista, p, cuadro):
        l, r = self.lienzo, self.recursos
        l.rect(SALA_X - 2, SALA_Y - 2, SALA_ANCHO + 4, SALA_ALTO + 4, (8, 8, 10))
        l.imagen(self._textura_sala, SALA_X, SALA_Y, SALA_ANCHO, SALA_ALTO)
        y_cara = SUELO_Y + SUELO_ALTO
        for i, x in enumerate([SALA_X + 136, SALA_X + 440]):         # antorchas (solo visual)
            l.imagen(r.resplandores[(cuadro // 2 + i) % 3], x - 48, y_cara - 30, 96, 96)
            l.imagen(r.antorchas[(cuadro + i) % 4], x - 16, y_cara + 12, 32, 32)
        self.puertas(vista, p)
        self.trampas(vista, p)

    #  Trampas

    HUECOS_TRAMPA = [SALA_X + 174, SALA_X + 356, SALA_X + 60, SALA_X + 470]

    def trampas(self, vista, p):
        """Lanzadardos en el muro y placa de presión en el suelo por cada trampa de la sala.

        Solo lee el estado: cuando una trampa pasa de armada a disparada, lanza
        la animación de los dardos (no toca la simulación).
        """
        l, r = self.lienzo, self.recursos
        clave = [p.cripta_id, p.semilla]
        if clave != self._clave_trampas:
            self._clave_trampas = clave
            self._disparadas = []
            self._dardos = []
        y_muro = SUELO_Y + SUELO_ALTO + 24
        for i, trampa in enumerate(getattr(p, "trampas", []) or []):
            x = self.HUECOS_TRAMPA[i % len(self.HUECOS_TRAMPA)]
            if not trampa.activa and trampa.id not in self._disparadas:
                self._disparadas.append(trampa.id)
                self._dardos.append([x, y_muro + 9, vista.animacion])
            elif trampa.activa and trampa.id in self._disparadas:
                self._disparadas.remove(trampa.id)            # se rearmó
            estado = 1 if trampa.activa else 0
            l.imagen(r.lanzadardos[estado], x - 14, y_muro, 28, 18)
            l.imagen(r.placa_presion[estado], x - 16, SUELO_Y + SUELO_ALTO - 26, 32, 16)
            if trampa.activa and int(vista.animacion * 2) % 2 == 0:
                l.elipse(x, y_muro + 9, 34, 22, (204, 52, 46, 40))   # brillo de amenaza
            nombre = trampa.tipo.split("_", 1)[-1].replace("_", " ") if trampa.tipo else "trampa"
            ayuda = (f"Trampa de {nombre} · armada · daño {trampa.dano}" if trampa.activa
                     else f"Trampa de {nombre} · disparada, se rearma sola")
            if l.bajo_raton(x - 16, SUELO_Y + SUELO_ALTO - 26, 32, 70):
                l.ayuda = ayuda                     # solo informa: no es clickeable

    def dardos_en_vuelo(self, vista):
        """Tres dardos que salen del muro hacia el jugador (0.45 s, solo visual)."""
        l = self.lienzo
        px, py = self.posicion_jugador(vista)
        vigentes = []
        for x0, y0, inicio in self._dardos:
            t = vista.animacion - inicio
            if t > 0.6:
                continue
            vigentes.append([x0, y0, inicio])
            for k, dx in enumerate([-6, 0, 6]):
                avance = min(1.0, max(0.0, (t - k * 0.06) / 0.35))
                if avance <= 0 or avance >= 1:
                    continue
                x = x0 + dx + (px - x0) * avance
                y = y0 + (py + 22 - y0) * avance
                distancia = max(1.0, math.hypot(px - x0, py + 22 - y0))
                ux = (px - x0) / distancia
                uy = (py + 22 - y0) / distancia
                for paso in range(8):                   # punta, astil y plumas rojas
                    color = (220, 220, 230) if paso < 2 else (130, 90, 52) if paso < 6 else (200, 40, 36)
                    tam = 3 if paso < 2 or paso >= 6 else 2
                    l.rect(x - ux * paso * 2, y - uy * paso * 2, tam, tam, color)
        self._dardos = vigentes

    @staticmethod
    def rect_puerta(direccion):
        """Rectángulo virtual de cada puerta: [x, y, ancho, alto]."""
        centro_x = SALA_X + SALA_ANCHO / 2
        centro_y = SUELO_Y + SUELO_ALTO / 2
        if direccion == "N":
            return [centro_x - 32, SUELO_Y + SUELO_ALTO, 64, 80]
        if direccion == "S":
            return [centro_x - 32, SALA_Y - 8, 64, 44]
        if direccion == "O":
            return [SALA_X, centro_y - 34, 32, 68]
        return [SALA_X + SALA_ANCHO - 32, centro_y - 34, 32, 68]

    def puertas(self, vista, p):
        l, r = self.lienzo, self.recursos
        for salida in p.vecindad:
            x, y, ancho, alto = self.rect_puerta(salida.direccion)
            if salida.es_salida_final:
                l.imagen(r.resplandor_oro, x + ancho / 2 - 48, y + alto / 2 - 48, 96, 96)
            l.imagen(r.puerta(salida.direccion, salida.cerrada, salida.es_salida_final), x, y, ancho, alto)
            if salida.cerrada:
                cx, cy = x + ancho / 2, y + alto / 2
                l.imagen(r.candado, cx - 7, cy - 9, 14, 18)
            encima = l.bajo_raton(x, y, ancho, alto)
            if encima or (getattr(vista, "modo_mover", False) and not salida.cerrada):
                parpadeo = int(vista.animacion * 4) % 2 == 0 or encima
                if parpadeo:
                    l.marco(x - 2, y - 2, ancho + 4, alto + 4, ORO, 2)
            destino = f"sala {salida.sala_id} · {salida.nombre}"
            if salida.cerrada:
                ayuda = f"Abrir {salida.direccion} ({destino}) · requiere llave"
            else:
                ayuda = f"Ir al {salida.direccion}: {destino}"
            if salida.es_salida_final:
                ayuda += " · ¡SALIDA!"
            l.zona(x, y, ancho, alto, "abrir" if salida.cerrada else "mover", salida.direccion, ayuda)

    #  Personajes y objetos

    def posicion_jugador(self, vista):
        x = SUELO_X + SUELO_ANCHO * 0.36 + 16
        if vista.pausa_visual and vista.accion_visual == "mover":
            x -= vista.pausa_visual * 60
        return [x, SUELO_Y + SUELO_ALTO * 0.40]

    def posicion(self, p, clase, id_):
        """Centro de los pies de una entidad en el suelo."""
        x, y = self.distribucion.posicion(p.sala_actual_id, clase, id_, SUELO_X, SUELO_Y, SUELO_ANCHO, SUELO_ALTO)
        return [x + 16, y]

    def entidades(self, vista, p, cuadro):
        """Objetos, enemigos y jugador, de atrás hacia adelante."""
        self.objetos(vista, p)
        self.enemigos(vista, p, cuadro)
        self.jugador(vista, p, cuadro)

    def personaje(self, textura, referencia, cx, pies, izquierda=False):
        """Dibuja al doble de tamaño manteniendo los pies y el centro del cuerpo.

        Returns:
            Altura del cuerpo dibujado (para ubicar la barra de vida).
        """
        caja = referencia.image.getbbox() or [0, 0, referencia.width, referencia.height]
        if izquierda:
            caja = [referencia.width - caja[2], caja[1], referencia.width - caja[0], caja[3]]
        ancho_cuerpo = (caja[2] - caja[0]) * K
        x = cx - ancho_cuerpo / 2 - caja[0] * K
        y = pies - (referencia.height - caja[3]) * K
        self.lienzo.imagen(textura, x, y, textura.width * K, textura.height * K)
        return (caja[3] - caja[1]) * K

    def jugador(self, vista, p, cuadro):
        """Dibuja al jugador orientado al objetivo, con su animación actual."""
        r = self.recursos
        px, py = self.posicion_jugador(vista)
        objetivo = next((pos for pos in self.distribucion.posiciones
                         if pos[:3] == [p.sala_actual_id, "enemigo", vista.enemigo]), None)
        izquierda = objetivo is not None and self.posicion(p, "enemigo", vista.enemigo)[0] < px
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
        animacion = (r.soldado_izquierda[accion] if izquierda else
                     [r.soldado_idle, r.soldado_correr, r.soldado_atacar, r.soldado_herido, r.soldado_morir][accion])
        indice = cuadro % len(animacion)
        if accion in [2, 3, 4]:
            indice = min(len(animacion) - 1, int(max(0, progreso) * len(animacion)))
        self.lienzo.elipse(px, py + 1, 24, 7, (0, 0, 0, 110))
        envenenado = any(str(e).startswith("Envenenado") for e in (p.efectos or []))
        if envenenado:
            self.burbujas_veneno(vista, px, py, detras=True)
        alto = self.personaje(animacion[indice], r.soldado_idle[0], px, py, izquierda=izquierda)
        if envenenado:
            self.burbujas_veneno(vista, px, py, detras=False)
        if vista.pausa_visual and vista.cambio_vida:
            self.numero(vista.cambio_vida, px, py + alto + 4, vista.pausa_visual, vista.duracion_visual)

    def burbujas_veneno(self, vista, px, py, detras):
        """Aura y burbujas verdes que suben y revientan alrededor del jugador envenenado."""
        l = self.lienzo
        t = vista.animacion
        if detras:
            pulso = 0.5 + 0.5 * math.sin(t * 4)
            l.elipse(px, py + 2, 40 + 8 * pulso, 12 + 3 * pulso, (60, 200, 70, int(60 + 50 * pulso)))
            l.elipse(px, py + 22, 30 + 6 * pulso, 46, (60, 220, 70, int(18 + 22 * pulso)))   # halo tóxico
        for k in range(14):
            fase = (t * 0.5 + k * 0.29) % 1.0
            atras = k % 2 == 0                      # mitad por detrás, mitad por delante
            if atras != detras:
                continue
            x = px + math.sin(k * 2.3 + t * 1.7) * (9 + k % 4 * 4)
            y = py + 2 + fase * 58
            radio = 2.5 + (k % 3) * 1.2 + (1.5 if fase > 0.85 else 0)
            alfa = int(220 * (1 - fase) ** 0.6)
            if fase > 0.92:                         # revienta
                for dx, dy in [[-4, 0], [4, 0], [0, 4], [0, -4], [-3, 3], [3, 3]]:
                    l.rect(x + dx, y + dy, 2, 2, (150, 255, 140, max(alfa, 90)))
                continue
            l.elipse(x, y, radio * 2 + 2, radio * 2 + 2, (20, 70, 24, alfa))
            l.elipse(x, y, radio * 2, radio * 2, (80, 220, 70, alfa))
            l.elipse(x - radio * 0.35, y + radio * 0.35, radio * 0.7, radio * 0.7, (210, 255, 200, alfa))

    def numero(self, valor, x, y, pausa, duracion=0.65):
        """Cambio de vida flotante con signo y color de daño o curación."""
        y += (duracion - pausa) * 24
        color = VERDE if valor > 0 else (255, 90, 80)
        self.lienzo.texto(f"{valor:+}", x, y, 2, color, negrita=True, ancla="centro", sombra=True)

    def enemigos(self, vista, p, cuadro):
        """Enemigos orientados al jugador; conserva un momento a los que acaban de morir."""
        l, r = self.lienzo, self.recursos
        jugador_x = self.posicion_jugador(vista)[0]
        transcurrido = max(0, vista.duracion_visual - vista.pausa_visual)
        visibles = p.enemigos + (vista.enemigos_muertos if vista.pausa_visual else [])
        # Los de atrás primero: los monstruos grandes se superponen bien.
        visibles = ordenar(visibles, key=lambda e: -self.posicion(p, "enemigo", e.id)[1])
        for enemigo in visibles:
            cx, pies = self.posicion(p, "enemigo", enemigo.id)
            atacando = vista.pausa_visual > 0 and enemigo.id in vista.atacantes
            muerto = enemigo in vista.enemigos_muertos
            herido = vista.pausa_visual > 0 and any(id_ == enemigo.id and cambio < 0 for id_, cambio in vista.cambios_enemigos)
            estado = "muerto" if muerto else "herido" if herido and (not atacando or transcurrido >= 0.325) else ""
            izquierda = cx > jugador_x
            cuadros = r.enemigo(enemigo, atacar=atacando, izquierda=izquierda, estado=estado)
            progreso = transcurrido / 0.65
            if muerto:
                progreso = transcurrido / vista.duracion_visual
            elif herido and atacando:
                progreso = (transcurrido - 0.325) / 0.325 if estado else transcurrido / 0.325
            indice = min(len(cuadros) - 1, int(max(0, progreso) * len(cuadros))) if atacando or estado else cuadro % len(cuadros)
            seleccionado = enemigo.id == vista.enemigo
            if seleccionado and not muerto:
                pulso = 160 + int(80 * math.sin(vista.animacion * 6))
                l.elipse(cx, pies + 1, 34, 11, (210, 50, 44, pulso), borde=2)
            l.elipse(cx, pies + 1, 26, 7, (0, 0, 0, 110))
            alto = self.personaje(cuadros[indice], r.enemigo(enemigo)[0], cx, pies, izquierda=izquierda)
            if muerto:
                continue
            barra_y = pies + alto + 6
            l.rect(cx - 13, barra_y - 1, 26, 6, (10, 8, 8))
            l.rect(cx - 12, barra_y, 24, 4, (60, 30, 28))
            l.rect(cx - 12, barra_y, 24 * enemigo.vida / max(1, enemigo.vida_max), 4, ROJO)
            if atacando:
                l.rect(cx - 12, pies - 4, 24, 2, ROJO)
            zona = l.zona(cx - 22, pies - 4, 44, alto + 14, "seleccionar", enemigo.id,
                          f"{enemigo.nombre} · {enemigo.vida}/{enemigo.vida_max} · doble clic: atacar")
            if seleccionado or zona.contiene(*l.raton):
                nombre = fp.recortar(enemigo.nombre, 120)
                ancho = fp.ancho_texto(nombre) + 6
                l.rect(cx - ancho / 2, barra_y + 7, ancho, 11, (10, 9, 12, 200))
                l.texto(nombre, cx, barra_y + 9, 1, TEXTO, ancla="centro")
        if vista.pausa_visual:
            for id_, cambio in vista.cambios_enemigos:
                if cambio and any(pos[:3] == [p.sala_actual_id, "enemigo", id_] for pos in self.distribucion.posiciones):
                    cx, pies = self.posicion(p, "enemigo", id_)
                    self.numero(cambio, cx, pies + 46, vista.pausa_visual, vista.duracion_visual)

    def objetos(self, vista, p):
        """Objetos que flotan sobre el suelo con una zona de recogida estable."""
        l, r = self.lienzo, self.recursos
        for i, objeto in enumerate(p.objetos_suelo):
            cx, y = self.posicion(p, "objeto", objeto.id)
            flotacion = 4 + math.sin(vista.animacion * 3 + i) * 2
            icono = r.icono(objeto)
            escala = 20 / max(icono.width, icono.height)
            ancho, alto = icono.width * escala, icono.height * escala
            l.elipse(cx, y + 2, 18, 5, (0, 0, 0, 120))
            l.imagen(icono, cx - ancho / 2, y + flotacion, ancho, alto)
            zona = l.zona(cx - 14, y - 2, 28, 30, "recoger", objeto.id, f"Recoger {objeto.nombre}")
            if zona.contiene(*l.raton):
                l.marco(cx - 14, y - 2, 28, 30, (214, 170, 82, 160), 1)

    #  Minimapa y mensaje

    def minimapa(self, vista, p):
        """Sala actual y vecinas; un clic en una vecina mueve (si la puerta está abierta)."""
        l = self.lienzo
        x0, y0 = SUELO_X + SUELO_ANCHO - 76, SUELO_Y + 6
        l.rect(x0, y0, 70, 60, (10, 9, 12, 170))
        l.marco(x0, y0, 70, 60, (70, 64, 56, 200))
        celda_x, celda_y = x0 + 25, y0 + 21
        l.rect(celda_x, celda_y, 20, 18, ORO)
        l.texto(str(p.sala_actual_id), celda_x + 10, celda_y + 6, 1, FONDO, ancla="centro")
        for vecina in p.vecindad:
            dx, dy = next([a, b] for d, a, b in [["N", 0, 20], ["S", 0, -20], ["O", -24, 0], ["E", 24, 0]]
                          if d == vecina.direccion)
            color = ROJO if vecina.cerrada else ORO if vecina.es_salida_final else (150, 140, 120)
            x, y = celda_x + dx, celda_y + dy
            encima = l.bajo_raton(x, y, 20, 18)
            l.rect(x, y, 20, 18, (40, 36, 32) if not encima else (70, 60, 44))
            l.marco(x, y, 20, 18, color)
            l.texto(str(vecina.sala_id), x + 10, y + 6, 1, color, ancla="centro")
            l.zona(x, y, 20, 18, "mover_mapa", vecina.direccion,
                   f"{vecina.direccion}: sala {vecina.sala_id}" + (" (cerrada)" if vecina.cerrada else ""))

    def mensaje_estado(self, vista):
        """Último aviso de la vista (acción rechazada, instrucciones) sobre el muro inferior."""
        if not vista.mensaje:
            return
        l = self.lienzo
        texto = fp.recortar(vista.mensaje, SALA_ANCHO - 140)
        ancho = fp.ancho_texto(texto) + 14
        x = SALA_X + (SALA_ANCHO - ancho) / 2
        y = SUELO_Y + SUELO_ALTO - 20
        l.rect(x, y, ancho, 15, (10, 9, 12, 215))
        l.texto(texto, x + 7, y + 4, 1, TEXTO)

    #  Panel lateral

    def inventario(self, vista, inventario):
        """Casillas grandes con iconos, como en el diseño de referencia."""
        l, r = self.lienzo, self.recursos
        l.panel(PANEL_X, PANEL_Y, PANEL_ANCHO, PANEL_ALTO)
        x0, tope = PANEL_X + 12, PANEL_Y + PANEL_ALTO - 12
        l.texto("INVENTARIO", x0, tope - 14, 2, (210, 200, 176), negrita=True)
        l.rect(x0, tope - 20, PANEL_ANCHO - 24, 2, (70, 64, 56))
        criterio = getattr(vista, "criterio", "real")
        l.texto(f"{inventario.tamano}/{inventario.capacidad}", x0, tope - 32, 1, TEXTO_SUAVE)
        orden = f"ORDEN: {criterio.upper()}"
        ancho_orden = fp.ancho_texto(orden) + 8
        x_orden = PANEL_X + PANEL_ANCHO - 12 - ancho_orden
        encima = l.bajo_raton(x_orden, tope - 35, ancho_orden, 12)
        l.rect(x_orden, tope - 35, ancho_orden, 12, (60, 50, 36) if encima else (34, 32, 34))
        l.texto(orden, x_orden + 4, tope - 32, 1, ORO if encima else TEXTO_SUAVE)
        l.zona(x_orden, tope - 35, ancho_orden, 12, "ordenar", "", "Cambiar el orden de la vista")

        items = getattr(inventario, f"vista_por_{criterio}")() if criterio != "real" else inventario.items()
        columnas = 4 if inventario.capacidad <= 12 else 5
        filas = max(1, math.ceil(inventario.capacidad / columnas))
        hueco = 4
        lado = min(40, (PANEL_ANCHO - 24 - (columnas - 1) * hueco) / columnas, (112 - (filas - 1) * hueco) / filas)
        arriba = tope - 42
        for i in range(inventario.capacidad):
            x = x0 + (i % columnas) * (lado + hueco)
            y = arriba - lado - (i // columnas) * (lado + hueco)
            item = items[i] if i < len(items) else None
            seleccionado = item is not None and item.instancia_id == vista.item
            encima = l.bajo_raton(x, y, lado, lado)
            l.rect(x, y, lado, lado, ORO if seleccionado else (70, 64, 56) if encima else (46, 43, 40))
            l.rect(x + 1, y + 1, lado - 2, lado - 2, (14, 13, 16))
            l.rect(x + 2, y + 2, lado - 4, lado - 4, (40, 34, 28) if seleccionado else (26, 25, 29))
            if item is None:
                continue
            icono = r.icono(item)
            escala = (lado - 10) / max(icono.width, icono.height)
            ancho_i, alto_i = icono.width * escala, icono.height * escala
            l.imagen(icono, x + (lado - ancho_i) / 2, y + (lado - alto_i) / 2, ancho_i, alto_i)
            if item.equipado:
                l.rect(x + 2, y + 2, 9, 10, (10, 9, 12, 220))
                l.texto("E", x + 4, y + 3, 1, ORO, negrita=True)
            l.zona(x, y, lado, lado, "seleccionar_item", item.instancia_id,
                   f"{item.nombre} · peso {item.peso} · valor {item.valor}")
        y_botones = arriba - filas * (lado + hueco) - 34
        seleccionado = inventario.buscar_por_id(vista.item)
        nombre = seleccionado.nombre if seleccionado else "Selecciona un objeto"
        l.texto(fp.recortar(nombre, PANEL_ANCHO - 24), x0, y_botones + 22, 1, ORO if seleccionado else TEXTO_SUAVE)
        ancho_boton = (PANEL_ANCHO - 24 - 8) / 3
        for i, (etiqueta, accion, tecla) in enumerate([["USAR", "usar", "U"], ["EQUIPAR", "equipar", "E"],
                                                       ["SOLTAR", "soltar", "S"]]):
            l.boton(x0 + i * (ancho_boton + 4), y_botones, ancho_boton, 16, etiqueta, accion, negrita=False,
                    activo=self.accion_activa == accion, ayuda=f"{etiqueta.capitalize()} [{tecla}]")
        vista.inventario_fondo = y_botones - 8

    def bitacora(self, vista, mensajes):
        """Últimos mensajes con desplazamiento; el más reciente abajo."""
        l = self.lienzo
        x0 = PANEL_X + 12
        tope = getattr(vista, "inventario_fondo", PANEL_Y + 190)
        l.texto("BITÁCORA", x0, tope - 16, 2, (210, 200, 176), negrita=True)
        l.rect(x0, tope - 22, PANEL_ANCHO - 24, 2, (70, 64, 56))
        alto_linea = 11
        y_inicio = tope - 36
        cantidad = max(1, int((y_inicio - (PANEL_Y + 8)) / alto_linea) + 1)
        lineas = lineas_bitacora(mensajes, PANEL_ANCHO - 24)
        vista.bitacora_limite = max(0, len(lineas) - cantidad)
        vista.bitacora_desplazamiento = min(vista.bitacora_desplazamiento, vista.bitacora_limite)
        fin = len(lineas) - vista.bitacora_desplazamiento
        visibles = lineas[max(0, fin - cantidad):fin]
        for i, texto in enumerate(visibles):
            reciente = vista.bitacora_desplazamiento == 0 and i >= len(visibles) - 2
            l.texto(texto, x0, y_inicio - i * alto_linea, 1, TEXTO if reciente else (184, 174, 150))
        l.zona(PANEL_X, PANEL_Y, PANEL_ANCHO, y_inicio - PANEL_Y + 8, "bitacora", "",
               "Rueda del ratón: ver mensajes anteriores" if vista.bitacora_limite else "")

    #  Barra inferior

    def hud(self, vista, p):
        l, r = self.lienzo, self.recursos
        l.panel(BARRA_X, BARRA_Y, BARRA_ANCHO, BARRA_ALTO)
        l.imagen(r.corazon, BARRA_X + 12, BARRA_Y + 30, 33, 30)
        x_barra, y_barra, ancho_barra = BARRA_X + 54, BARRA_Y + 44, 156
        l.rect(x_barra - 2, y_barra - 2, ancho_barra + 4, 16, (8, 8, 10))
        l.rect(x_barra, y_barra, ancho_barra, 12, (58, 30, 28))
        lleno = ancho_barra * max(0, p.jugador_vida) / max(1, p.jugador_vida_max)
        l.rect(x_barra, y_barra, lleno, 12, ROJO)
        l.rect(x_barra, y_barra + 9, lleno, 3, (150, 36, 32))
        l.rect(x_barra, y_barra, lleno, 2, (236, 96, 86))
        l.texto(f"VIDA {p.jugador_vida}/{p.jugador_vida_max}", x_barra, BARRA_Y + 24, 2, (214, 206, 186), negrita=True)
        efectos = " · ".join(p.efectos) if p.efectos else ""
        if efectos:
            l.texto(fp.recortar(efectos, 200), BARRA_X + 12, BARRA_Y + 11, 1, ORO)
        else:
            l.texto(f"ATQ {p.jugador_ataque} · DEF {p.jugador_defensa} · VEL {p.jugador_velocidad}",
                    BARRA_X + 12, BARRA_Y + 11, 1, TEXTO_SUAVE)
        l.rect(BARRA_X + 222, BARRA_Y + 10, 2, BARRA_ALTO - 20, (52, 48, 44))
        x = BARRA_X + 232
        for etiqueta, accion, icono, ayuda in [["MOVER", "modo_mover", r.icono_mover, "Mover: flechas o clic en una puerta"],
                                               ["ATACAR", "atacar", r.icono_atacar, "Atacar al enemigo seleccionado [A]"],
                                               ["ESPERAR", "esperar", r.icono_esperar, "Esperar [.]"]]:
            activo = self.accion_activa == accion or (accion == "modo_mover" and getattr(vista, "modo_mover", False))
            l.boton(x, BARRA_Y + 12, 146, 46, etiqueta, accion, icono=icono, activo=activo, tam=2, ayuda=ayuda)
            x += 152
        for accion, icono, ayuda in [["retroceder", r.icono_pergamino, "Pergamino de retroceso [P]"],
                                     ["menu", r.icono_salir, "Menú, sala y ayuda [Esc]"]]:
            l.boton(x, BARRA_Y + 12, 40, 46, "", accion, icono=icono, activo=self.accion_activa == accion, ayuda=ayuda)
            x += 44
