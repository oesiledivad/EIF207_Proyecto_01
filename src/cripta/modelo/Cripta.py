


class Cripta:
    """El mundo del juego: reglas generales y la lista de salas.
    No sabe de HTTP ni de JSON."""

    def __init__(self, id, version, sala_inicial, sala_salida, llave_salida,
                 presupuesto_solicitudes, inventario_max, salas=None):
        self.id = id
        self.version = version
        self.sala_inicial = sala_inicial
        self.sala_salida = sala_salida
        self.llave_salida = llave_salida
        self.presupuesto_solicitudes = presupuesto_solicitudes
        self.inventario_max = inventario_max
        self.salas = salas if salas is not None else []
    def obtener_sala(self, id_sala):
        sala = self.salas[id_sala - 1]
        if sala.id != id_sala:
            raise ValueError(f"Los ids de sala no son contiguos: se pidió {id_sala}")
        return sala
    def resumen(self):
        return (f"Cripta {self.id} (v{self.version}) — {len(self.salas)} salas, "
                f"inicial={self.sala_inicial}, salida={self.sala_salida}")