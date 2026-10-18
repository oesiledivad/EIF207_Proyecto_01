"""Música de ambientación de la vista gráfica: solo decora, nunca toca la simulación."""
from pathlib import Path

import arcade


#  Música de ambientación (propia, generada con herramientas/generar_musica.py)

_MUSICA = Path(__file__).resolve().parents[1] / "recursos" / "musica"
_PISTAS = [
    ["menu", _MUSICA / "menu.wav"],
    ["cripta", _MUSICA / "cripta.wav"],
    ["combate", _MUSICA / "combate.wav"],
]


class Musica:
    """Una pista en bucle a la vez; cambiar de pista corta la anterior."""

    def __init__(self, activo=True, volumen=0.8):
        self.activo = activo
        self.volumen = volumen
        self.actual = ""
        self._reproductor = None
        self._cargadas = []          # pares [nombre, sonido]; sin dict

    def _buscar(self, nombre):
        for clave, sonido in self._cargadas:
            if clave == nombre:
                return sonido
        ruta = next((r for n, r in _PISTAS if n == nombre), None)
        if ruta is None or not ruta.is_file():
            return None
        sonido = arcade.load_sound(ruta)
        self._cargadas.append([nombre, sonido])
        return sonido

    def poner(self, nombre):
        """Cambia a la pista `nombre` ("" = silencio). Si ya suena, no la reinicia."""
        if nombre == self.actual:
            return
        self.detener()
        self.actual = nombre
        if not self.activo or not nombre:
            return
        try:
            sonido = self._buscar(nombre)
            if sonido is not None:
                self._reproductor = arcade.play_sound(sonido, volume=self.volumen, loop=True)
        except Exception:        # sin dispositivo de audio: el juego sigue en silencio
            self.activo = False

    def detener(self):
        if self._reproductor is not None:
            try:
                arcade.stop_sound(self._reproductor)
            except Exception:
                pass
        self._reproductor = None

    def alternar(self):
        """Silencia o reanuda la música (tecla F3)."""
        self.activo = not self.activo
        pista = self.actual
        self.actual = ""
        if self.activo:
            self.poner(pista)
        else:
            self.detener()
            self.actual = pista
        return self.activo
