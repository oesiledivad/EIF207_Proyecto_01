"""Resultado de una acción del controlador.

Se usa en lugar de dict para devolver el estado de una operación a la
vista, manteniendo consistencia con el resto de DTOs y evitando el uso
de dict como estructura propia (§7).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ResultadoAccion:
    """Resultado de una acción ejecutada por el controlador.

    Attributes:
        ok: True si la acción se completó.
        motivo: Explicación si ok es False.
        datos: Información adicional opcional (item, mensaje, etc.).
    """

    ok: bool
    motivo: str = ""
    datos: Any = None

    @classmethod
    def exito(cls, datos: Any = None) -> "ResultadoAccion":
        """Construye un resultado exitoso.

        Args:
            datos: Información adicional opcional.

        Returns:
            ResultadoAccion con ok=True.
        """
        return cls(ok=True, datos=datos)

    @classmethod
    def fallo(cls, motivo: str) -> "ResultadoAccion":
        """Construye un resultado fallido.

        Args:
            motivo: Explicación del fallo.

        Returns:
            ResultadoAccion con ok=False.
        """
        return cls(ok=False, motivo=motivo)