# Música

Pistas propias, sintetizadas con `herramientas/generar_musica.py` (solo biblioteca
estándar de Python). No usan muestras ni obras de terceros.

- `menu.wav`: pad en re menor, bordón grave y caja de música con eco (32 s en bucle).
- `cripta.wav`: exploración; bordón, viento, gotas de agua y campana lejana (40 s).
- `combate.wav`: tambor grave a 96 ppm, bajo ostinato y cuerdas con trémolo (30 s).

Formato: WAV mono, 16 bits, 16 kHz. Para cambiarlas, editar el generador y volver a
ejecutarlo: `uv run python herramientas/generar_musica.py`.
