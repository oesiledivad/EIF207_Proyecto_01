# Fuente Cripta Pixel

Fuente pixel original del proyecto (5x7, con tildes y ñ). Los glifos están en
`grafica/fuente_pixel.py`; los `.ttf` se generan con:

    uv run --with fonttools python herramientas/generar_fuente.py

La vista mide los textos con esas mismas tablas, así que el texto ocupa lo
mismo en Windows, macOS y Linux sin importar cómo cada sistema dibuje fuentes.
