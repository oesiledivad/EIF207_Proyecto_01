"""Efectos de sonido de la vista gráfica: solo decoran, nunca tocan la simulación."""
from pathlib import Path

import arcade

_PROPIOS = Path(__file__).resolve().parents[1] / "recursos" / "sonidos"

# Sonidos incluidos con arcade (pack de Kenney, dominio público CC0) y propios.
_ARCHIVOS = [
    ["portal", _PROPIOS / "portal.wav"],          # cambio de sala: campanas místicas (propio)
    ["golpe", ":resources:sounds/hit1.wav"],
    ["herido", ":resources:sounds/hurt1.wav"],
    ["muerte_enemigo", ":resources:sounds/explosion2.wav"],
    ["recoger", ":resources:sounds/coin1.wav"],
    ["usar", ":resources:sounds/upgrade1.wav"],
    ["puerta", ":resources:sounds/rockHit2.wav"],
    ["retroceso", ":resources:sounds/phaseJump1.wav"],
    ["error", ":resources:sounds/error1.wav"],
    ["derrota", ":resources:sounds/gameover1.wav"],
    ["victoria", ":resources:sounds/secret2.wav"],
]


class Sonidos:
    """Carga los sonidos la primera vez que se usan y permite silenciarlos."""

    def __init__(self, activo=True, volumen=0.5):
        self.activo = activo
        self.volumen = volumen
        self._cargados = []          # pares [nombre, sonido]; sin dict

    def _buscar(self, nombre):
        for clave, sonido in self._cargados:
            if clave == nombre:
                return sonido
        ruta = next((r for n, r in _ARCHIVOS if n == nombre), None)
        if ruta is None:
            return None
        sonido = arcade.load_sound(ruta)
        self._cargados.append([nombre, sonido])
        return sonido

    def tocar(self, nombre):
        """Reproduce un efecto; si no hay audio disponible, el juego sigue en silencio."""
        if not self.activo:
            return
        try:
            sonido = self._buscar(nombre)
            if sonido is not None:
                arcade.play_sound(sonido, volume=self.volumen)
        except Exception:        # sin tarjeta de sonido, archivo faltante, etc.
            self.activo = False

    def alternar(self):
        self.activo = not self.activo
        return self.activo

    def cambiar_volumen(self, volumen):
        """Limita el volumen de los próximos efectos al rango de 0 a 1."""
        self.volumen = max(0, min(1, round(volumen, 2)))
