"""Genera los efectos de sonido propios del juego (solo hace falta al cambiarlos).

    uv run python herramientas/generar_sonidos.py

Usa solo la biblioteca estándar (wave + math): el sonido es síntesis original,
sin archivos de terceros ni licencias.
"""
import math
import struct
import wave
from pathlib import Path

FRECUENCIA = 22050
DESTINO = Path(__file__).resolve().parents[1] / "src" / "cripta" / "vista" / "recursos" / "sonidos"


def campana(muestras, inicio, frecuencia, volumen, decaimiento):
    """Suma una nota tipo campana: fundamental + parcial inarmónico + leve desafinación (brillo)."""
    primera = int(inicio * FRECUENCIA)
    for i in range(primera, len(muestras)):
        t = (i - primera) / FRECUENCIA
        envolvente = min(1.0, t / 0.008) * math.exp(-t / decaimiento)
        if envolvente < 1e-4:
            break
        onda = (math.sin(2 * math.pi * frecuencia * t)
                + 0.6 * math.sin(2 * math.pi * frecuencia * 1.004 * t)       # vibración suave
                + 0.25 * math.sin(2 * math.pi * frecuencia * 2.76 * t) * math.exp(-t / 0.15))
        muestras[i] += volumen * envolvente * onda


def portal():
    """Arpegio ascendente de campanas con un colchón grave y eco: suena 'místico'."""
    duracion = 1.9
    muestras = [0.0] * int(duracion * FRECUENCIA)
    for i in range(len(muestras)):                                       # colchón grave que crece y se va
        t = i / FRECUENCIA
        envolvente = math.sin(math.pi * min(1.0, t / 1.4)) ** 2 if t < 1.4 else 0.0
        muestras[i] += 0.18 * envolvente * (math.sin(2 * math.pi * 146.83 * t)
                                            + 0.5 * math.sin(2 * math.pi * 220.0 * t))
    for paso, nota in enumerate([587.33, 880.0, 1174.66, 1318.51, 1760.0]):   # Re5 La5 Re6 Mi6 La6
        campana(muestras, 0.05 + paso * 0.085, nota, 0.32 - paso * 0.03, 0.55)
    con_eco = list(muestras)
    for retraso, ganancia in [(0.19, 0.35), (0.38, 0.16)]:                # eco de cripta
        corrimiento = int(retraso * FRECUENCIA)
        for i in range(corrimiento, len(con_eco)):
            con_eco[i] += ganancia * muestras[i - corrimiento]
    final = int(0.25 * FRECUENCIA)                                       # cola sin chasquido
    for k in range(final):
        con_eco[-1 - k] *= k / final
    pico = max(abs(m) for m in con_eco) or 1.0
    return [m / pico * 0.6 for m in con_eco]


def guardar(nombre, muestras):
    DESTINO.mkdir(parents=True, exist_ok=True)
    ruta = DESTINO / nombre
    with wave.open(str(ruta), "wb") as archivo:
        archivo.setnchannels(1)
        archivo.setsampwidth(2)
        archivo.setframerate(FRECUENCIA)
        archivo.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, m)) * 32767)) for m in muestras))
    print("Sonido generado:", ruta.name, ruta.stat().st_size, "bytes")


if __name__ == "__main__":
    guardar("portal.wav", portal())
