"""Texturas cargadas una sola vez: personajes y armas de los packs, y arte propio."""
from pathlib import Path

import arcade

from . import heroe
from . import monstruos
from .assets import imagen
from .packs import animacion, armas

RECURSOS = Path(__file__).resolve().parents[1] / "recursos"
heroe_TIPOS = ["ninguna", "daga", "espada", "hacha", "lanza", "baston", "maza",
               "cuero", "placas", "manto", "malla"]   # tipos ya clasificados


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
        self.img_baldosas = [imagen(f"baldosa_{i}") for i in range(10)]
        self.img_ladrillos = [imagen(f"ladrillos_{i}") for i in range(4)]
        self.img_muro = [imagen(f"muro_{i}") for i in range(4)]
        self.img_borde = [imagen(f"borde_{i}") for i in range(4)]
        self.img_pilar = imagen("pilar")
        self.img_decoracion = [imagen(n) for n in ["barril", "vasija", "rocas", "calavera"]]
        # Tres intensidades del halo: el parpadeo alterna texturas (sin transparencia variable).
        self.resplandores = [_tex(imagen(f"resplandor_{i}")) for i in range(3)]
        self.resplandor_oro = _tex(imagen("resplandor_oro"))
        carpeta = RECURSOS / "catacombs"
        self.antorchas = [arcade.load_texture(carpeta / f"torch_{i}.png") for i in range(1, 5)]
        # Puertas: [direccion, abierta, cerrada, abierta-salida, cerrada-salida]
        self.puertas = []
        for direccion in ["N", "S", "O", "E"]:
            imagenes = [imagen(f"puerta_{direccion}_{int(cerrada)}_{int(salida)}")
                        for salida in [False, True] for cerrada in [False, True]]
            self.puertas.append([direccion, [_tex(i) for i in imagenes]])

    def puerta(self, direccion, cerrada, salida):
        cuadros = next(c for d, c in self.puertas if d == direccion)
        return cuadros[(2 if salida else 0) + (1 if cerrada else 0)]

    #  Interfaz

    def _interfaz(self):
        self.corazon = _tex(imagen("corazon"))
        self.candado = _tex(imagen("candado"))
        self.icono_mover = _tex(imagen("cruceta"))
        self.icono_atacar = _tex(imagen("espada"))
        self.icono_esperar = _tex(imagen("reloj"))
        self.icono_pergamino = _tex(imagen("pergamino"))
        self.icono_salir = _tex(imagen("puerta_salir"))
        # Trampas: [desarmada, armada]
        self.lanzadardos = [_tex(imagen("lanzadardos_0")), _tex(imagen("lanzadardos_1"))]
        self.placa_presion = [_tex(imagen("placa_presion_0")), _tex(imagen("placa_presion_1"))]

    #  Objetos

    def _objetos(self):
        self.pocion_roja = _tex(imagen("pocion"))
        self.pocion_azul = _tex(imagen("pocion_B"))
        self.pocion_violeta = _tex(imagen("pocion_U"))
        self.antidoto = _tex(imagen("pocion_V"))
        self.llave = _tex(imagen("llave"))
        self.antorcha = _tex(imagen("antorcha"))
        self.pergamino = _tex(imagen("pergamino"))
        self.armadura = _tex(imagen("armadura"))
        self.gema = _tex(imagen("gema"))
        self.gema_azul = _tex(imagen("gema_B"))
        self.cofre = _tex(imagen("cofre"))
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

    #  Personajes: héroe propio y enemigos con respaldo si faltan packs.

    def _personajes(self):
        self._heroes = []
        self.heroe()                    # el jugador sin equipo queda listo desde el inicio
        # Personajes de los packs (solo los que estén instalados en recursos/local).
        self.personajes = []
        self.ataques = []
        self.heridos = []
        self.muertes = []
        for n in ["Orc", "Demon_A", "Blood Monster_A", "Soldier"]:
            reposo = animacion(n, "Idle")
            if reposo:
                self._agregar(n, [reposo, animacion(n, "Attack01") or reposo,
                                  animacion(n, "Hurt") or reposo, animacion(n, "Death") or reposo])
        # Arte propio: los enemigos de las criptas publicadas (más grandes y tenebrosos que
        # los "chibi" de los packs) y el espectro de respaldo para cualquier tipo desconocido.
        self._agregar("Rata", monstruos.rata())
        self._agregar("Esqueleto", monstruos.esqueleto())
        for comportamiento in ["rastreador", "errante", "guardián", ""]:
            self._agregar(f"Espectro {comportamiento}", monstruos.espectro(comportamiento))

        def reflejar(coleccion):
            return [[n, [t.flip_left_right() for t in c]] for n, c in coleccion]
        self.personajes_izquierda = reflejar(self.personajes)
        self.ataques_izquierda = reflejar(self.ataques)
        self.heridos_izquierda = reflejar(self.heridos)
        self.muertes_izquierda = reflejar(self.muertes)

    def heroe(self, arma="ninguna", armadura="ninguna", antorcha=False, izquierda=False):
        """Animaciones del jugador con ese equipo: [reposo, caminar, atacar, herido, muerte].

        Se cargan la primera vez que aparece cada combinación y se reutilizan
        (lista de [clave, derecha, izquierda]; sin dict).
        """
        clave = [heroe.tipo_arma(arma) if arma not in heroe_TIPOS else arma,
                 heroe.tipo_armadura(armadura) if armadura not in heroe_TIPOS else armadura, bool(antorcha)]
        for guardada, derecha, reflejada in self._heroes:
            if guardada == clave:
                return reflejada if izquierda else derecha
        derecha = [[_tex(c) for c in cuadros] for cuadros in heroe.animaciones(*clave)]
        reflejada = [[t.flip_left_right() for t in cuadros] for cuadros in derecha]
        self._heroes.append([clave, derecha, reflejada])
        return reflejada if izquierda else derecha

    def _agregar(self, nombre, animaciones):
        """Registra [reposo, ataque, herida, muerte] (imágenes PIL o texturas) con un nombre."""
        texturas = [[c if isinstance(c, arcade.Texture) else _tex(c) for c in cuadros]
                    for cuadros in animaciones]
        colecciones = [self.personajes, self.ataques, self.heridos, self.muertes]
        for i in range(len(colecciones)):
            colecciones[i].append([nombre, texturas[i]])

    def nombre_enemigo(self, enemigo):
        """Qué arte usa un enemigo. Orden de respaldo:

        1. Arte propio por nombre o tipo (rata, esqueleto/óseo).
        2. Personaje de un pack si el tipo se parece y el pack está instalado.
        3. Espectro según el comportamiento (guardián, errante, rastreador).
        4. Espectro genérico.
        """
        tipo = f"{getattr(enemigo, 'tipo', '')} {getattr(enemigo, 'nombre', '')}".lower()
        disponibles = [n for n, _ in self.personajes]
        for palabras, nombre in [[["rata", "ratón", "raton", "roedor"], "Rata"],
                                 [["óseo", "oseo", "esqueleto", "hueso", "calavera", "osario"], "Esqueleto"],
                                 [["orco", "orc", "acechador"], "Orc"],
                                 [["demon", "custodio"], "Demon_A"],
                                 [["sangre", "sombra"], "Blood Monster_A"],
                                 [["guardia", "soldado", "patrullero"], "Soldier"]]:
            if any(p in tipo for p in palabras) and nombre in disponibles:
                return nombre
        comportamiento = (getattr(enemigo, "comportamiento", "") or "").lower().replace("guardian", "guardián")
        if f"Espectro {comportamiento}" in disponibles:
            return f"Espectro {comportamiento}"
        return "Espectro "

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
        nombre = self.nombre_enemigo(enemigo)
        return next(c for n, c in coleccion if n == nombre)
