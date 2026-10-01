
from .jugadorDto import Jugador

class Crypta_Details:
    def __init__(self, id, version, salas, pages, room_start, room_exit,
                 key, solicitudes, inventario, jugador: Jugador) -> None:
        self.id = id
        self.version = version
        self.salas = salas
        self.pages = pages
        self.room_start = room_start
        self.room_exit = room_exit
        self.key = key
        self.solicitudes = solicitudes
        self.inventario = inventario
        self.jugador = jugador

    @staticmethod
    def since_dict(d: dict) -> "Crypta_Details":
        return Crypta_Details(
            id=d["id"],
            version=d["version"],
            salas=d["salas_total"],
            pages=d["paginas"],
            room_start=d["sala_inicial"],
            room_exit=d["sala_salida"],
            key=d["llave_salida"],
            solicitudes=d["presupuesto_solicitudes"],
            inventario=d["inventario_max"],
            jugador=Jugador.desde_dict(d["jugador"]),
        )