# modelo/Sala.py

from cripta.estructuras.Salidas import Salidas

class SalaJuego:
    """Entidad de dominio: una sala jugable, con enemigos y objetos ya resueltos.

    Todas las salas del esqueleto se crean al iniciar la partida (vacías).
    Su contenido (enemigos dormidos, objetos, trampas) se incorpora después,
    cuando llega por lotes desde la red (§4.2). `contenido_cargado` indica si
    eso ya pasó.
    """

    def __init__(self, id: int, nombre: str, salidas: Salidas,
                 enemigos: list, objetos: list, trampas: list) -> None:
        self.id = id
        self.nombre = nombre
        self.salidas = salidas      # Salidas (estructura propia, sin dict)
        self.enemigos = enemigos    # list[Enemigo] (Modelo, ya ensamblados)
        self.objetos = objetos      # list[ObjetoSuelo]
        self.trampas = trampas      # list[TrampaJuego]
        self.ultimo_tiempo_visita: int | None = None
        self.contenido_cargado = False

    def agregar_enemigo(self, enemigo, historial=None) -> None:
        """O(1) amortizado."""
        if historial is None:
            self.enemigos.append(enemigo)
        else:
            historial.agregar(self.enemigos, enemigo)

    def quitar_enemigo(self, enemigo, historial=None) -> None:
        """O(k), k = enemigos en la sala (pocos). Compara por identidad."""
        i = 0
        while i < len(self.enemigos):
            if self.enemigos[i] is enemigo:
                if historial is None:
                    self.enemigos.pop(i)
                else:
                    historial.quitar(self.enemigos, enemigo)
                return
            i += 1
