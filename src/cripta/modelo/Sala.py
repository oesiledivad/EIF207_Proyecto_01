# modelo/Sala.py

class SalaJuego:
    """Entidad de dominio: una sala jugable, con enemigos y objetos ya resueltos."""

    def __init__(self, id: int, nombre: str, salidas: dict,
                 enemigos: list, objetos: list, trampas: list) -> None:
        self.id = id
        self.nombre = nombre
        self.salidas = salidas      # dict: direccion(str) -> Salida (DTO, reusado tal cual)
        self.enemigos = enemigos    # list[Enemigo] (Modelo, ya ensamblados)
        self.objetos = objetos      # list[Item] (Modelo, ya ensamblados)
        self.trampas = trampas      # list[TrampaDto] (por ahora, DTO crudo)
        self.ultimo_tiempo_visita: int | None = None