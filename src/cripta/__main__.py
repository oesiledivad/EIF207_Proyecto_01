"""Punto de entrada del paquete.

Solo delega en el bootstrap. Nada de lógica aquí.
"""

from cripta.bootstrap import main


if __name__ == "__main__":
    raise SystemExit(main())