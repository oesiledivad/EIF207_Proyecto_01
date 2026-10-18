"""Genera la música de ambientación (src/cripta/vista/recursos/musica/*.wav).

Música propia sintetizada solo con la biblioteca estándar (sin licencias):

- menu.wav     "Osario": pad lento en re menor, bordón grave y una caja de
               música lejana con eco.
- cripta.wav   exploración: bordón que late, viento, gotas de agua y una
               campana lejana. Casi sin melodía para no cansar.
- combate.wav  tensión: tambor grave a 96 pulsos por minuto, bajo ostinato y
               cuerdas disonantes con trémolo.

Cada pista es un bucle sin corte: lo que suena después del final (ecos,
colas) se mezcla con el comienzo. Uso:

    uv run python herramientas/generar_musica.py
"""
import math
import random
import struct
import wave
from pathlib import Path

TASA = 16000
DESTINO = Path(__file__).resolve().parents[1] / "src" / "cripta" / "vista" / "recursos" / "musica"


def nota(nombre: str) -> float:
    """'D3' -> frecuencia en Hz (afinación La4 = 440)."""
    orden = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    letra, octava = nombre[:-1], int(nombre[-1])
    semitonos = orden.index(letra) - 9 + (octava - 4) * 12
    return 440.0 * 2 ** (semitonos / 12)


class Pista:
    """Buffer de muestras en flotante; las voces se suman encima."""

    def __init__(self, segundos: float, cola: float = 4.0):
        self.largo = int(segundos * TASA)
        self.muestras = [0.0] * (self.largo + int(cola * TASA))

    def sumar(self, inicio: float, duracion: float, generador) -> None:
        a = int(inicio * TASA)
        n = int(duracion * TASA)
        for i in range(n):
            j = a + i
            if j >= len(self.muestras):
                break
            self.muestras[j] += generador(i / TASA)

    def eco(self, retardo: float, ganancia: float, repeticiones: int = 4) -> None:
        d = int(retardo * TASA)
        for i in range(d, len(self.muestras)):
            self.muestras[i] += self.muestras[i - d] * ganancia

    def bucle(self, pico: float, archivo: Path) -> None:
        """Mezcla la cola sobre el comienzo, normaliza y guarda WAV mono de 16 bits."""
        datos = self.muestras[:self.largo]
        cola = self.muestras[self.largo:]
        for i, valor in enumerate(cola):
            datos[i % self.largo] += valor
        maximo = max(abs(v) for v in datos) or 1.0
        escala = pico / maximo
        archivo.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(archivo), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(TASA)
            w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v * escala)) * 32767)) for v in datos))
        print(f"{archivo.name}: {len(datos) / TASA:.1f} s")


def envolvente(t: float, ataque: float, duracion: float, salida: float) -> float:
    if t < ataque:
        return t / ataque
    if t > duracion - salida:
        return max(0.0, (duracion - t) / salida)
    return 1.0


def pad(frecuencia: float, duracion: float, volumen: float, brillo: float = 0.3):
    """Cuerdas suaves: tres osciladores desafinados con armónicos y ataque lento."""
    def g(t):
        e = envolvente(t, duracion * 0.35, duracion, duracion * 0.4)
        s = 0.0
        for desafino in [0.997, 1.0, 1.004]:
            f = frecuencia * desafino
            s += math.sin(2 * math.pi * f * t) + brillo * math.sin(4 * math.pi * f * t) / 2 \
                + brillo * 0.5 * math.sin(6 * math.pi * f * t) / 3
        return s * e * volumen / 3
    return g


def campana(frecuencia: float, volumen: float, caida: float = 1.6):
    def g(t):
        e = math.exp(-t / (caida / 3)) * min(1.0, t * 400)
        return volumen * e * (math.sin(2 * math.pi * frecuencia * t) * 0.7
                              + math.sin(2 * math.pi * frecuencia * 2.76 * t) * 0.2 * math.exp(-t * 3)
                              + math.sin(2 * math.pi * frecuencia * 5.4 * t) * 0.1 * math.exp(-t * 6))
    return g


def bordon(frecuencia: float, duracion: float, volumen: float, latido: float = 0.15):
    def g(t):
        e = envolvente(t, 2.0, duracion, 2.0)
        lfo = 0.75 + 0.25 * math.sin(2 * math.pi * latido * t)
        return volumen * e * lfo * (math.sin(2 * math.pi * frecuencia * t)
                                    + 0.5 * math.sin(2 * math.pi * frecuencia * 1.5 * t + 0.3)
                                    + 0.25 * math.sin(2 * math.pi * frecuencia * 2.003 * t))
    return g


def menu() -> None:
    p = Pista(32)
    acordes = [["D3", "F3", "A3"], ["A#2", "D3", "F3"], ["G2", "A#2", "D3"], ["A2", "C#3", "E3"]]
    for i, acorde in enumerate(acordes):
        for n in acorde:
            p.sumar(i * 8, 10, pad(nota(n), 10, 0.22))
    p.sumar(0, 34, bordon(nota("D2"), 34, 0.25, 0.1))
    melodia = [[0, "D5"], [1.5, "F5"], [3, "A5"], [5, "G5"], [6.5, "F5"],
               [8, "D5"], [9.5, "A#4"], [11, "D5"], [13, "F5"],
               [16, "G5"], [17.5, "A#5"], [19, "A5"], [21, "G5"], [22.5, "D5"],
               [24, "E5"], [25.5, "C#5"], [27, "E5"], [29, "A4"]]
    for t, n in melodia:
        p.sumar(t, 2.5, campana(nota(n), 0.16))
    p.eco(0.42, 0.33)
    p.bucle(0.55, DESTINO / "menu.wav")


def cripta() -> None:
    azar = random.Random(7)
    p = Pista(40)
    p.sumar(0, 42, bordon(nota("D2"), 42, 0.3, 0.07))
    p.sumar(0, 42, bordon(nota("A1"), 42, 0.18, 0.11))
    # Viento: ruido filtrado con ráfagas lentas.
    filtrado = 0.0
    for i in range(p.largo):
        t = i / TASA
        filtrado += (azar.uniform(-1, 1) - filtrado) * 0.02
        rafaga = 0.5 + 0.5 * math.sin(2 * math.pi * t / 40 * 3) * math.sin(2 * math.pi * t / 40 * 2 + 1)
        p.muestras[i] += filtrado * 0.9 * (0.3 + 0.7 * rafaga)
    # Gotas de agua.
    for _ in range(14):
        inicio = azar.uniform(0.5, 38)
        f0 = azar.uniform(1300, 2100)
        p.sumar(inicio, 0.18, lambda t, f0=f0: 0.12 * math.exp(-t * 28)
                * math.sin(2 * math.pi * (f0 * t - 2600 * t * t)))
    # Campana lejana y unas notas sueltas, muy suaves.
    for t, n in [[3, "D4"], [13, "A3"], [23, "F4"], [33, "C4"]]:
        p.sumar(t, 4, campana(nota(n), 0.12, 3.0))
    for t, n in [[8, "A4"], [8.9, "F4"], [28, "G4"], [28.9, "E4"]]:
        p.sumar(t, 3, pad(nota(n), 3, 0.07, 0.1))
    p.eco(0.55, 0.38)
    p.bucle(0.5, DESTINO / "cripta.wav")


def combate() -> None:
    p = Pista(30, cola=2.0)
    pulso = 60 / 96                                              # 48 pulsos = 30 s exactos
    for b in range(48):
        t = b * pulso
        fuerte = b % 4 == 0
        p.sumar(t, 0.4, lambda x, v=0.55 if fuerte else 0.32: v * math.exp(-x * 9)
                * math.sin(2 * math.pi * (70 * x - 45 * x * x)))                    # tambor grave
        if b % 2 == 1:
            p.sumar(t, 0.08, lambda x: 0.06 * math.exp(-x * 60) * math.sin(2 * math.pi * 3100 * x))  # golpe metálico
    ostinato = ["D2", "D2", "F2", "D2", "E2", "D2", "A#1", "C#2"]
    for b in range(96):
        t = b * pulso / 2
        f = nota(ostinato[b % 8])
        p.sumar(t, pulso / 2, lambda x, f=f: 0.22 * math.exp(-x * 5)
                * (math.sin(2 * math.pi * f * x) + 0.4 * math.sin(4 * math.pi * f * x)))
    acordes = [["D4", "D#4", "A4"], ["C#4", "D4", "G#4"], ["D4", "F4", "B4"], ["C#4", "E4", "A#4"]]
    for i, acorde in enumerate(acordes):
        for n in acorde:
            f = nota(n)
            p.sumar(i * 7.5, 7.5, lambda x, f=f: 0.07 * (0.6 + 0.4 * math.sin(2 * math.pi * 6 * x))
                    * envolvente(x, 0.8, 7.5, 1.0)
                    * (math.sin(2 * math.pi * f * x) + 0.5 * math.sin(4 * math.pi * f * x)))
    p.eco(pulso * 0.75, 0.2)
    p.bucle(0.6, DESTINO / "combate.wav")


if __name__ == "__main__":
    menu()
    cripta()
    combate()
