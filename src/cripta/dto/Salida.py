from dataclasses import dataclass

@dataclass
class Salida:
    """Una salida dirigida de una sala (estado inicial, no vivo)."""
    sala: int
    cerrada: bool | None = None
    llave: str | None = None
    cierre_automatico: int | None = None