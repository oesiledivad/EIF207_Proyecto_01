"""Texturas de Catacombs y packs locales, cargadas una sola vez."""
from pathlib import Path
from PIL import Image

import arcade
from .packs import animacion, armas
from .catacumbas import cargar


RECURSOS = Path(__file__).resolve().parents[1] / "recursos"


class Recursos:
    """Centraliza texturas, animaciones y versiones orientadas a la izquierda."""

    def __init__(self):
        """Carga los recursos una vez y prepara alternativas si faltan packs locales."""
        cargar(self)
        self.soldado_idle = animacion("Soldier", "Idle") or [self.estatua]
        self.soldado_correr = animacion("Soldier", "Walk") or self.soldado_idle
        self.soldado_atacar = animacion("Soldier", "Attack01") or self.soldado_idle
        self.soldado_herido = animacion("Soldier", "Hurt") or self.soldado_idle
        self.soldado_morir = animacion("Soldier", "Death") or self.soldado_idle
        self.soldado_izquierda = [[t.flip_left_right() for t in cuadros]
                                 for cuadros in [self.soldado_idle, self.soldado_correr, self.soldado_atacar,
                                                 self.soldado_herido, self.soldado_morir]]
        self.personajes = [[nombre, animacion(nombre, "Idle") or [self.estatua]]
                           for nombre in ["Orc", "Demon_A", "Blood Monster_A", "Soldier"]]
        self.ataques = [[nombre, animacion(nombre, "Attack01") or cuadros]
                       for nombre, cuadros in self.personajes]
        self.personajes_izquierda = [[n, [t.flip_left_right() for t in c]] for n, c in self.personajes]
        self.ataques_izquierda = [[n, [t.flip_left_right() for t in c]] for n, c in self.ataques]
        self.heridos = [[n, animacion(n, "Hurt") or c] for n, c in self.personajes]
        self.muertes = [[n, animacion(n, "Death") or c] for n, c in self.personajes]
        self.heridos_izquierda = [[n, [t.flip_left_right() for t in c]] for n, c in self.heridos]
        self.muertes_izquierda = [[n, [t.flip_left_right() for t in c]] for n, c in self.muertes]
        iconos = armas()
        if iconos:
            self.espada, self.hacha, self.daga, self.baston, self.lanza = iconos
        self.puertas = self.cargar_puertas()

    @staticmethod
    def cargar_puertas():
        """Devuelve las puertas abiertas y cerradas de cada dirección, con marco común."""
        with Image.open(RECURSOS / "generados" / "puertas.png") as imagen:
            imagen = imagen.convert("RGBA")
            ancho, alto = [imagen.width // 4, imagen.height // 2]
            puertas = []
            for direccion, col in [["N", 0], ["S", 1], ["E", 3], ["O", 2]]:
                cuadros = [imagen.crop([col * ancho, fila * alto, (col + 1) * ancho, (fila + 1) * alto])
                           for fila in range(2)]
                cajas = [c.getbbox() for c in cuadros]
                borde = [min(c[0] for c in cajas), min(c[1] for c in cajas),
                         max(c[2] for c in cajas), max(c[3] for c in cajas)]
                puertas.append([direccion, [arcade.Texture(c.crop(borde)) for c in cuadros]])
        return puertas

    def enemigo(self, enemigo, atacar=False, izquierda=False, estado=""):
        """Elige una animación por identidad, orientación y estado visual.

        Args:
            enemigo: Enemigo con tipo y nombre del catálogo.
            atacar: Selecciona el ataque cuando no hay daño o muerte prioritarios.
            izquierda: Usa los cuadros reflejados horizontalmente.
            estado: Vacío, herido o muerto.

        Returns:
            list: Cuadros reutilizables de la animación elegida.
        """
        if izquierda:
            coleccion = self.ataques_izquierda if atacar else self.personajes_izquierda
        else:
            coleccion = self.ataques if atacar else self.personajes
        if estado in ["herido", "muerto"]:
            if estado == "herido":
                coleccion = self.heridos_izquierda if izquierda else self.heridos
            else:
                coleccion = self.muertes_izquierda if izquierda else self.muertes
        tipo = f"{enemigo.tipo} {enemigo.nombre}".lower()
        for palabra, nombre in [["óseo", "Demon_A"], ["oseo", "Demon_A"], ["esqueleto", "Demon_A"],
                                ["orco", "Orc"], ["orc", "Orc"], ["demon", "Demon_A"],
                                ["sangre", "Blood Monster_A"], ["guardia", "Soldier"],
                                ["soldado", "Soldier"], ["patrullero", "Soldier"],
                                ["acechador", "Orc"], ["custodio", "Demon_A"],
                                ["sombra", "Blood Monster_A"]]:
            if palabra in tipo:
                cuadros = next(c for n, c in coleccion if n == nombre)
                if cuadros:
                    return cuadros
        return next(c for n, c in coleccion if n == "Orc")

    def icono(self, item):
        """Devuelve el icono de un objeto por su clase, tipo o nombre."""
        clase = getattr(item, "clase", "")
        tipo = f"{item.tipo_id} {item.nombre}".lower()
        for palabra, textura in [["antidoto", self.antidoto], ["antídoto", self.antidoto],
                                 ["lanza", self.lanza], ["hacha", self.hacha],
                                 ["daga", self.daga], ["baston", self.baston],
                                 ["bastón", self.baston], ["antorcha", self.baston],
                                 ["llave", self.cofre], ["pocion", self.objeto],
                                 ["poción", self.objeto]]:
            if palabra in tipo:
                return textura
        if clase == "arma" or "hoja" in tipo or "espada" in tipo:
            return self.espada
        if clase == "pocion":
            return self.objeto
        return self.cofre if clase == "llave" else self.caja


