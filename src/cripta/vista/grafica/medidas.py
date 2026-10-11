"""Medidas del lienzo virtual y cálculo de escala (sin dependencias gráficas).

La interfaz se diseña una sola vez en 800x450 y se escala para cada ventana.
Con esto se ve igual en una laptop con el escalado de Windows al 150 % que en
un monitor grande: cambia el tamaño en píxeles, nunca las proporciones.
"""

ANCHO = 800
ALTO = 450


def calcular_escala(ancho_ventana: float, alto_ventana: float) -> tuple[float, int, int]:
    """Escala y márgenes para que el lienzo quepa centrado en la ventana.

    Si la escala es casi entera (pierde menos del 10 %) se usa la entera, para
    que cada píxel del arte mida lo mismo y se vea nítido.

    Returns:
        (escala, margen_x, margen_y)
    """
    escala = min(ancho_ventana / ANCHO, alto_ventana / ALTO)
    entera = int(escala)
    if entera >= 1 and entera / escala >= 0.9:
        escala = float(entera)
    escala = max(0.1, escala)
    return escala, round((ancho_ventana - ANCHO * escala) / 2), round((alto_ventana - ALTO * escala) / 2)


def tamano_ventana_inicial(pantalla_ancho: int, pantalla_alto: int) -> tuple[int, int]:
    """Tamaño inicial proporcional a la pantalla (16:9, hasta 90 % x 85 %).

    Si cabe un múltiplo entero de 800x450 se usa ese (pixel art nítido).
    """
    limite_ancho, limite_alto = pantalla_ancho * 0.9, pantalla_alto * 0.85
    entero = int(min(limite_ancho / ANCHO, limite_alto / ALTO))
    if entero >= 2:
        return ANCHO * entero, ALTO * entero
    escala = max(0.8, min(limite_ancho / ANCHO, limite_alto / ALTO))
    return int(ANCHO * escala), int(ALTO * escala)
