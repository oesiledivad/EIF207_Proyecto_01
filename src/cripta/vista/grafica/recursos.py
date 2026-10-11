"""Texturas cargadas una sola vez: personajes y armas de los packs, y arte propio."""
from pathlib import Path

import arcade

from . import pixelart as pa
from .packs import animacion, armas

RECURSOS = Path(__file__).resolve().parents[1] / "recursos"


def _tex(imagen):
    return arcade.Texture(imagen)


class Recursos:
    """Centraliza texturas, animaciones y versiones orientadas a la izquierda."""

    def __init__(self):
        """Carga los recursos una vez y prepara alternativas si faltan packs locales."""
        self._sala()
        self._interfaz()
        self._objetos()
        self._personajes()

    #  Sala

    def _sala(self):
        # Imágenes PIL: la escena compone con ellas una sola textura por sala.
        self.img_baldosas = [pa.baldosa(i) for i in range(10)]
        self.img_ladrillos = [pa.ladrillos(i) for i in range(4)]
        self.img_muro = [pa.bloque_muro(i) for i in range(4)]
        self.img_borde = [pa.bloque_muro(i, 16, 8) for i in range(4)]
        self.img_pilar = pa.pilar(40)
        self.img_decoracion = [pa.dibujo(d) for d in [pa.BARRIL, pa.VASIJA, pa.ROCAS, pa.CALAVERA]]
        # Tres intensidades del halo: el parpadeo alterna texturas (sin transparencia variable).
        self.resplandores = [_tex(pa.resplandor(48, fuerza=f)) for f in (0.7, 0.85, 1.0)]
        self.resplandor = self.resplandores[-1]
        self.resplandor_oro = _tex(pa.resplandor(32, (255, 210, 110)))
        carpeta = RECURSOS / "catacombs"
        self.antorchas = [arcade.load_texture(carpeta / f"torch_{i}.png") for i in range(1, 5)]
        # Puertas: [direccion, abierta, cerrada, abierta-salida, cerrada-salida]
        self.puertas = []
        for direccion, fabrica in [["N", pa.puerta_norte], ["S", pa.puerta_sur],
                                   ["O", pa.puerta_lateral], ["E", pa.puerta_lateral]]:
            imagenes = [fabrica(cerrada, salida) for salida in (False, True) for cerrada in (False, True)]
            if direccion == "E":
                imagenes = [i.transpose(0) for i in imagenes]   # reflejo horizontal
            self.puertas.append([direccion, [_tex(i) for i in imagenes]])

    def puerta(self, direccion, cerrada, salida):
        cuadros = next(c for d, c in self.puertas if d == direccion)
        return cuadros[(2 if salida else 0) + (1 if cerrada else 0)]

    #  Interfaz

    def _interfaz(self):
        self.corazon = _tex(pa.dibujo(pa.CORAZON))
        self.candado = _tex(pa.dibujo(pa.CANDADO))
        self.icono_mover = _tex(pa.dibujo(pa.CRUCETA))
        self.icono_atacar = _tex(pa.dibujo(pa.ESPADA))
        self.icono_esperar = _tex(pa.dibujo(pa.RELOJ))
        self.icono_pergamino = _tex(pa.dibujo(pa.PERGAMINO))
        self.icono_sala = _tex(pa.dibujo(pa.LUPA))
        self.icono_salir = _tex(pa.dibujo(pa.PUERTA_SALIR))

    #  Objetos

    def _objetos(self):
        self.pocion_roja = _tex(pa.dibujo(pa.POCION))
        self.pocion_azul = _tex(pa.con_color(pa.POCION, "B"))
        self.pocion_violeta = _tex(pa.con_color(pa.POCION, "U"))
        self.antidoto = _tex(pa.con_color(pa.POCION, "V"))
        self.llave = _tex(pa.dibujo(pa.LLAVE))
        self.antorcha = _tex(pa.dibujo(pa.ANTORCHA))
        self.pergamino = _tex(pa.dibujo(pa.PERGAMINO))
        self.armadura = _tex(pa.dibujo(pa.ARMADURA))
        self.gema = _tex(pa.dibujo(pa.GEMA))
        self.gema_azul = _tex(pa.con_color(pa.GEMA, "B"))
        self.cofre = _tex(pa.dibujo(pa.COFRE))
        iconos = armas()
        if iconos:
            self.espada, self.hacha, self.daga, self.baston, self.lanza = iconos
        else:
            self.espada = self.hacha = self.daga = self.baston = self.lanza = self.icono_atacar

    def icono(self, item):
        """Icono de un objeto por su clase (inventario) o por su id/nombre (suelo)."""
        clase = getattr(item, "clase", "") or ""
        texto = f"{getattr(item, 'tipo_id', '')} {getattr(item, 'id', '')} {item.nombre}".lower()
        for palabras, textura in [
            [["antidoto", "antídoto"], self.antidoto],
            [["velocidad", "rapid", "rápid", "prisa"], self.pocion_azul],
            [["pesadez", "lent"], self.pocion_violeta],
            [["llave"], self.llave],
            [["pergamino"], self.pergamino],
            [["dosis", "pocion", "poción", "elixir", "frasco"], self.pocion_roja],
            [["zafiro"], self.gema_azul],
            [["esfera", "rubi", "rubí", "gema"], self.gema],
            [["antorcha", "luz", "fabrial"], self.antorcha],
            [["lanza"], self.lanza], [["hacha"], self.hacha], [["daga"], self.daga],
            [["baston", "bastón"], self.baston],
            [["coraza", "armadura", "manto", "escudo", "cota"], self.armadura],
            [["espada", "hoja"], self.espada],
            [["pocion", "poción"], self.pocion_roja],
        ]:
            if any(p in texto for p in palabras):
                return textura
        for nombre_clase, textura in [["arma", self.espada], ["armadura", self.armadura],
                                      ["pocion", self.pocion_roja], ["llave", self.llave],
                                      ["antorcha", self.antorcha], ["antidoto", self.antidoto],
                                      ["pergamino_retroceso", self.pergamino]]:
            if clase == nombre_clase:
                return textura
        return self.cofre

    #  Personajes (packs de Zerie; si faltan se usa una estatua)

    def _personajes(self):
        respaldo = [_tex(pa.dibujo(pa.CALAVERA))]
        self.soldado_idle = animacion("Soldier", "Idle") or respaldo
        self.soldado_correr = animacion("Soldier", "Walk") or self.soldado_idle
        self.soldado_atacar = animacion("Soldier", "Attack01") or self.soldado_idle
        self.soldado_herido = animacion("Soldier", "Hurt") or self.soldado_idle
        self.soldado_morir = animacion("Soldier", "Death") or self.soldado_idle
        self.soldado_izquierda = [[t.flip_left_right() for t in cuadros]
                                  for cuadros in [self.soldado_idle, self.soldado_correr, self.soldado_atacar,
                                                  self.soldado_herido, self.soldado_morir]]
        nombres = ["Orc", "Demon_A", "Blood Monster_A", "Soldier"]
        self.personajes = [[n, animacion(n, "Idle") or respaldo] for n in nombres]
        self.ataques = [[n, animacion(n, "Attack01") or c] for n, c in self.personajes]
        self.heridos = [[n, animacion(n, "Hurt") or c] for n, c in self.personajes]
        self.muertes = [[n, animacion(n, "Death") or c] for n, c in self.personajes]

        def reflejar(coleccion):
            return [[n, [t.flip_left_right() for t in c]] for n, c in coleccion]
        self.personajes_izquierda = reflejar(self.personajes)
        self.ataques_izquierda = reflejar(self.ataques)
        self.heridos_izquierda = reflejar(self.heridos)
        self.muertes_izquierda = reflejar(self.muertes)

    def enemigo(self, enemigo, atacar=False, izquierda=False, estado=""):
        """Elige una animación por identidad, orientación y estado visual."""
        if estado == "herido":
            coleccion = self.heridos_izquierda if izquierda else self.heridos
        elif estado == "muerto":
            coleccion = self.muertes_izquierda if izquierda else self.muertes
        elif atacar:
            coleccion = self.ataques_izquierda if izquierda else self.ataques
        else:
            coleccion = self.personajes_izquierda if izquierda else self.personajes
        tipo = f"{getattr(enemigo, 'tipo', '')} {enemigo.nombre}".lower()
        for palabra, nombre in [["óseo", "Demon_A"], ["oseo", "Demon_A"], ["esqueleto", "Demon_A"],
                                ["orco", "Orc"], ["orc", "Orc"], ["demon", "Demon_A"],
                                ["sangre", "Blood Monster_A"], ["guardia", "Soldier"],
                                ["soldado", "Soldier"], ["patrullero", "Soldier"],
                                ["acechador", "Orc"], ["custodio", "Demon_A"],
                                ["sombra", "Blood Monster_A"], ["rata", "Blood Monster_A"]]:
            if palabra in tipo:
                return next(c for n, c in coleccion if n == nombre)
        return next(c for n, c in coleccion if n == "Orc")
