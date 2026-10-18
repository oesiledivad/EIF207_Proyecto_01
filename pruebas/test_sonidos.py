"""Configuración de audio comprobada antes de importar Arcade."""
import os
import subprocess
import sys
import unittest


class PruebasAudio(unittest.TestCase):
    def ejecutar(self, codigo, audio=None):
        """Usa un proceso nuevo para comprobar el orden real de importación."""
        entorno = os.environ.copy()
        entorno.pop("PYGLET_AUDIO", None)
        if audio is not None:
            entorno["PYGLET_AUDIO"] = audio
        resultado = subprocess.run([sys.executable, "-B", "-c", codigo],
                                   env=entorno, capture_output=True, text=True, timeout=30)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)

    @unittest.skipUnless(sys.platform == "win32", "Configuración específica de Windows")
    def test_configura_antes_de_importar_media(self):
        self.ejecutar('''
import sys
import cripta.vista.grafica
import pyglet
assert "pyglet.media" not in sys.modules
assert list(pyglet.options["audio"]) == ["directsound", "openal", "silent"]
import arcade
from pyglet.media.drivers import get_audio_driver
assert "xaudio2" not in type(get_audio_driver()).__module__
''')

    def test_respeta_audio_configurado_por_entorno(self):
        self.ejecutar('''
import cripta.vista.grafica
import pyglet
assert list(pyglet.options["audio"]) == ["silent"]
''', audio="silent")


if __name__ == "__main__":
    unittest.main()
