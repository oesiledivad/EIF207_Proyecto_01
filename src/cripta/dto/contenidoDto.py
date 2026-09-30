class EnemigoContenido:
    def __init__(self, instancia: str, tipo: str, vida: int = None) -> None:
        self.instancia = instancia
        self.tipo = tipo
        self.vida = vida

    @staticmethod
    def desde_dict(d: dict) -> "EnemigoContenido":
        return EnemigoContenido(
            instancia=d["instancia"],
            tipo=d["tipo"],
            vida=d.get("vida"),
        )


class TrampaContenido:
    def __init__(self, instancia: str, tipo: str) -> None:
        self.instancia = instancia
        self.tipo = tipo

    @staticmethod
    def desde_dict(d: dict) -> "TrampaContenido":
        return TrampaContenido(instancia=d["instancia"], tipo=d["tipo"])


class ContenidoSala:
    def __init__(self, sala: int, enemigos: list, objetos: list, trampas: list) -> None:
        self.sala = sala
        self.enemigos = enemigos
        self.objetos = objetos
        self.trampas = trampas

    @staticmethod
    def desde_dict(d: dict) -> "ContenidoSala":
        enemigos = []
        for e in d["enemigos"]:
            enemigos.append(EnemigoContenido.desde_dict(e))
        trampas = []
        for t in d["trampas"]:
            trampas.append(TrampaContenido.desde_dict(t))
        return ContenidoSala(
            sala=d["sala"],
            enemigos=enemigos,
            objetos=d["objetos"],
            trampas=trampas,
        )


class ContenidoRespuesta:
    def __init__(self, contenido: list) -> None:
        self.contenido = contenido

    @staticmethod
    def desde_dict(d: dict) -> "ContenidoRespuesta":
        contenido = []
        for c in d["contenido"]:
            contenido.append(ContenidoSala.desde_dict(c))
        return ContenidoRespuesta(contenido=contenido)