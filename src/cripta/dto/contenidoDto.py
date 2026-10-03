from dataclasses import dataclass


@dataclass
class EnemigoContenido:
    instancia: str
    tipo: str
    vida: int | None = None


@dataclass
class TrampaContenido:
    instancia: str
    tipo: str


@dataclass
class ContenidoSala:
    sala: int
    enemigos: list[EnemigoContenido] | None = None
    objetos: list[str] | None = None        # ids del catálogo
    trampas: list[TrampaContenido] | None = None

    def __post_init__(self):
        # 1. Si la API omitió alguna lista, la dejamos vacía
        if self.enemigos is None:
            self.enemigos = []
        if self.objetos is None:
            self.objetos = []
        if self.trampas is None:
            self.trampas = []

        # 2. Convertimos cada enemigo (dict) en EnemigoContenido
        enemigos_convertidos = []
        for datos in self.enemigos:
            if isinstance(datos, EnemigoContenido):
                enemigos_convertidos.append(datos)
            else:
                enemigos_convertidos.append(EnemigoContenido(**datos))
        self.enemigos = enemigos_convertidos

        # 3. Lo mismo con las trampas
        trampas_convertidas = []
        for datos in self.trampas:
            if isinstance(datos, TrampaContenido):
                trampas_convertidas.append(datos)
            else:
                trampas_convertidas.append(TrampaContenido(**datos))
        self.trampas = trampas_convertidas


@dataclass
class ContenidoRespuesta:
    """Respuesta completa de GET /criptas/{id}/contenido"""
    contenido: list[ContenidoSala]

    def __post_init__(self):
        salas_convertidas = []
        for datos in self.contenido:
            if isinstance(datos, ContenidoSala):
                salas_convertidas.append(datos)
            else:
                salas_convertidas.append(ContenidoSala(**datos))
        self.contenido = salas_convertidas