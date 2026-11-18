"""Ayudas para las pruebas de terreno y cazador (no es una prueba).

Cada prueba arma su propio esqueleto: aquí no hay ids ni datos de ninguna cripta concreta
(FR-028). Las salas se describen con `sala(...)` de `pruebas/apoyo_niebla.py`.

Hay tres ayudas:
    * `armar_modelo`: modelo puro sin `Aplicacion` (salas, entrantes, Simulacion, Jugador).
    * `FuenteCazador` y `armar_aplicacion_cazador`: una `Aplicacion` completa con fichas de
      enemigo (de cualquier comportamiento) definidas por la prueba.
    * `decision_desde_cero`: referencia lenta e independiente de la búsqueda de producción.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import FuenteNiebla, contenido, sala
from cripta.controlador.Aplicacion import Aplicacion
from cripta.estructuras.Historial_Retroceso import Historial_Retroceso
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Salidas import Salidas, indice_direccion
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.Simulacion import Simulacion
from cripta.modelo.enemigos.Cazador import Cazador
from cripta.modelo.enemigos.Errante import Errante
from cripta.modelo.enemigos.Guardian import Guardian
from cripta.modelo.enemigos.Rastreador import Rastreador

INFINITO = 10 ** 12
__all__ = ["sala", "contenido", "armar_modelo", "crear_enemigo", "programar", "turno",
           "decision_desde_cero", "ficha_enemigo", "FuenteCazador", "armar_aplicacion_cazador"]


class Modelo:
    """Salas, entrantes, simulación y jugador de una prueba sin `Aplicacion`."""

    def __init__(self, salas, entrantes, sim, jugador):
        self.salas = salas
        self.entrantes = entrantes
        self.sim = sim
        self.jugador = jugador
        self.enemigos = []


def armar_modelo(descripcion, sala_jugador, semilla=1, velocidad_jugador=100, con_historial=False):
    """Arma el modelo a partir de salas descritas con `sala(...)` y deja la persecución configurada."""
    maximo = 0
    for s in descripcion:
        if s["id"] > maximo:
            maximo = s["id"]
    salas = IndiceSalas()
    entrantes = [[] for _ in range(maximo + 1)]
    for s in descripcion:
        salidas = Salidas()
        for direccion, datos in s["salidas"].items():
            salidas.agregar(direccion, datos["sala"], datos.get("cerrada", False), datos.get("llave"),
                            datos.get("cierre_automatico"), datos.get("costo", 100))
        for salida in salidas:
            salida.clave = s["id"] * 4 + indice_direccion(salida.direccion)
            entrantes[salida.sala_destino].append(salida)
        salas.insertar(s["id"], SalaJuego(id=s["id"], nombre=s["nombre"], salidas=salidas,
                                          enemigos=[], objetos=[], trampas=[]))
    historial = Historial_Retroceso() if con_historial else None
    sim = Simulacion(semilla, historial)
    sim.persecucion.configurar(entrantes)
    jugador = Jugador("jugador", 30, 30, 6, 2, velocidad_jugador, sala_jugador, 0, 10)
    return Modelo(salas, entrantes, sim, jugador)


def crear_enemigo(modelo, comportamiento, id_, sala_id, velocidad=100, rango=0):
    """Crea un enemigo de ese comportamiento, lo pone en su sala y registra su rango si es cazador."""
    datos = (id_, 20, 20, 5, 1, velocidad, sala_id, None)
    if comportamiento == "cazador":
        enemigo = Cazador(*datos, rango=rango)
    elif comportamiento == "errante":
        enemigo = Errante(*datos)
    elif comportamiento == "rastreador":
        enemigo = Rastreador(*datos)
    else:
        enemigo = Guardian(*datos)
    modelo.salas.obtener(sala_id).enemigos.append(enemigo)
    modelo.enemigos.append(enemigo)
    return enemigo


def programar(modelo, enemigo, tiempo):
    """Deja al enemigo activo con su turno en `tiempo` (como `activar_enemigo`)."""
    agenda = modelo.sim.agenda
    evento = agenda.insertar(tiempo, enemigo, "accion_actor")
    enemigo._proximo_evento = evento
    enemigo.tiempo_siguiente = tiempo
    if enemigo.comportamiento == "cazador":
        modelo.sim.persecucion.registrar_rango(enemigo.rango)


def turno(modelo, enemigo):
    """Corre el turno pendiente del enemigo: adelanta el reloj y ejecuta su decisión."""
    modelo.sim.reloj.avanzar_hasta(enemigo.tiempo_siguiente)
    return modelo.sim._ejecutar_turno_enemigo(enemigo, modelo.jugador, modelo.salas)


def decision_desde_cero(salas, sala_cazador, sala_jugador, rango):
    """Referencia FR-011 a FR-014 sin reutilizar nada de producción: relajación hasta el punto fijo.

    Devuelve la salida que debe usar el cazador, o nada si espera.
    """
    todas = [s for s in salas._datos if s is not None]
    dist = [INFINITO] * len(salas._datos)
    dist[sala_jugador] = 0
    cambio = True
    while cambio:
        cambio = False
        for s in todas:
            for salida in s.salidas:
                if salida.cerrada:
                    continue
                candidata = salida.costo + dist[salida.sala_destino]
                if candidata < dist[s.id]:
                    dist[s.id] = candidata
                    cambio = True
    d = dist[sala_cazador]
    if d >= INFINITO or d > rango:
        return None
    mejor = None
    for salida in salas.obtener(sala_cazador).salidas:
        if salida.cerrada or dist[salida.sala_destino] >= INFINITO:
            continue
        if salida.costo + dist[salida.sala_destino] != d:
            continue
        llave = [salida.sala_destino, indice_direccion(salida.direccion)]
        if mejor is None or llave < mejor[0]:
            mejor = [llave, salida]
    return mejor[1] if mejor is not None else None


def ficha_enemigo(id_, comportamiento="cazador", rango=300, velocidad=100, vida_max=10, ataque=1):
    """Ficha de catálogo de un enemigo, como la entrega el servicio."""
    ficha = {"id": id_, "clase": "enemigo", "nombre": f"Enemigo {id_}", "vida_max": vida_max,
             "ataque": ataque, "defensa": 0, "velocidad": velocidad,
             "comportamiento": comportamiento, "suelta": None}
    if rango is not None:
        ficha["rango"] = rango
    return ficha


class FuenteCazador(FuenteNiebla):
    """Fuente falsa que agrega al catálogo las fichas que arma la prueba."""

    def __init__(self, salas, sala_inicial=1, sala_salida=None, contenidos=None, fichas=None):
        super().__init__(salas, sala_inicial, sala_salida, contenidos)
        self._fichas = fichas or []

    def get_catalog_version(self):
        return {"version": "catalogo-cazador-1"}

    def catalog(self, ids):
        entidades = []
        for id_ in ids:
            propia = None
            for ficha in self._fichas:
                if ficha["id"] == id_:
                    propia = ficha
            if propia is None:
                propia = super().catalog([id_])["entidades"][0]
            entidades.append(propia)
        return {"entidades": entidades}


def armar_aplicacion_cazador(salas, fichas, contenidos, sala_inicial=1, sala_salida=None,
                             ruta_guardado=None, carpeta_logs=None):
    """`Aplicacion` con la partida iniciada sobre el esqueleto, las fichas y el contenido de la prueba.

    Con `carpeta_logs` la partida se registra (para el replay); sin ella no se registra nada.
    """
    fuente = FuenteCazador(salas, sala_inicial, sala_salida, contenidos, fichas)
    app = Aplicacion(fuente, ruta_guardado=ruta_guardado, carpeta_logs=carpeta_logs)
    if carpeta_logs is None:
        resultado = app.iniciar_partida("Jugador", "42", "cripta-01", registrar=False, verificar=False)
    else:
        resultado = app.iniciar_partida("Jugador", "42", "cripta-01")
    if not resultado.ok:
        raise AssertionError(resultado.motivo)
    return app


def enemigos_en(id_sala, tipos):
    """Contenido de una sala con enemigos `[[instancia, tipo], ...]`."""
    return {"sala": id_sala,
            "enemigos": [{"instancia": i, "tipo": t} for i, t in tipos],
            "objetos": [], "trampas": []}
