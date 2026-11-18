"""Controlador de la línea de tiempo (spec 004).

Traduce la partida al vector de ranuras de `LineaTiempo` (research.md, D1 a D4):

- ranuras fijas 0 a 8: sala, vida, vida máxima, ataque, defensa y velocidad del jugador,
  resultado, inventario (tupla de textos) y efectos (tupla de textos);
- desde la 9: el conocimiento del jugador, n estados de sala y 4n memorias de salida;
- después, dos ranuras (sala y vida) por cada enemigo, creadas la primera vez que cambia.

Captura por evento: la simulación avisa al terminar cada evento y el ciclo de acciones avisa
después de ejecutar la acción y al cerrarla. Los enemigos que cambiaron llegan por el observador
del historial de retroceso; el conocimiento, por su registro cronológico (spec 002, FR-017).

Las consultas solo leen: no tocan el estado del juego, el azar, el historial ni partida.log (FR-007).
"""

from __future__ import annotations

from cripta.dto.Historia_dto import EnemigoInstante, ResultadoHistoria, ResumenInstante
from cripta.estructuras.Linea_Tiempo import CERCANO, LineaTiempo
from cripta.estructuras.Ordenamientos import ordenar
from cripta.modelo.Conocimiento import TIPO_ESTADO_SALA, ConocimientoJugador
from cripta.modelo.Enemigo import Enemigo

K_POR_DEFECTO = 50   # fijado con la medición L1 de --bench (research.md, D6 y D12)

R_SALA, R_VIDA, R_VIDA_MAX, R_ATAQUE, R_DEFENSA, R_VELOCIDAD = 0, 1, 2, 3, 4, 5
R_RESULTADO, R_INVENTARIO, R_EFECTOS = 6, 7, 8
R_CONOCIMIENTO = 9


def validar_k(valor) -> int:
    """Convierte y valida `--checkpoint-cada` (FR-017)."""
    texto = str(valor).strip()
    if not texto.isdigit() or int(texto) < 1:
        raise ValueError("--checkpoint-cada debe ser un entero mayor o igual que 1.")
    return int(texto)


def formatear_resumen(r: ResumenInstante) -> str:
    """Texto del resumen, el mismo para la vista y para --replay --hasta (FR-021)."""
    lineas = [f"Instante t={r.reloj} · acciones del jugador tomadas: {r.acciones}",
              f"Sala {r.sala_id}: {r.sala_nombre}",
              f"Vida {r.vida}/{r.vida_max} · Ataque {r.ataque} · Defensa {r.defensa} · "
              f"Velocidad {r.velocidad}",
              f"Partida: {r.resultado}",
              "Inventario: " + (", ".join(r.inventario) if r.inventario else "vacío"),
              "Efectos: " + (", ".join(r.efectos) if r.efectos else "ninguno"),
              "Enemigos en la sala: " + (", ".join(f"{e.nombre} ({e.id}) vida {e.vida}/{e.vida_max}"
                                                   for e in r.enemigos) if r.enemigos else "ninguno"),
              "Mapa conocido:"]
    for sala in r.mapa.exploradas:
        salidas = ", ".join(f"{s.direccion}>{s.destino} c{s.costo} {s.puerta.replace('_', ' ')}"
                            for s in sala.salidas)
        lineas.append(f"  {sala.id} {sala.nombre}: {salidas or 'sin salidas'}")
    lineas.append("  avistadas: " + (", ".join(str(i) for i in r.mapa.avistadas)
                                    if r.mapa.avistadas else "ninguna"))
    if r.aviso:
        lineas.append(r.aviso)
    return "\n".join(lineas)


class LineaTiempoControlador:
    """Mantiene la línea de tiempo de la partida activa y responde `historia`.

    Args:
        aplicacion: Contexto compartido de la partida.
        k: K de `--checkpoint-cada`; None usa el por defecto (o el guardado, al cargar).
    """

    def __init__(self, aplicacion, k: int | None = None) -> None:
        self._app = aplicacion
        self.k_solicitado = k
        self.linea: LineaTiempo | None = None
        self._n = 0
        self._cursor = 0
        self._enemigos: list = []
        self._ids: list[str] = []
        self._ranura_enemigo: list[int] = []
        self._sucios: list = []

    #  Ciclo de vida

    def iniciar(self) -> None:
        """Crea la línea en el instante 0, con el estado inicial de la partida."""
        app = self._app
        conocimiento = app._exploracion.conocimiento
        self._n = len(conocimiento.estado_sala) if conocimiento.inicializado else 0
        inicial = self._fijas()
        inicial.extend(conocimiento.estado_sala if conocimiento.inicializado else [])
        inicial.extend(conocimiento.puerta if conocimiento.inicializado else [])
        k = self.k_solicitado if self.k_solicitado is not None else K_POR_DEFECTO
        self.linea = LineaTiempo(k, inicial)
        self._cursor = len(conocimiento.registro) if conocimiento.inicializado else 0
        self._enemigos, self._ids, self._ranura_enemigo, self._sucios = [], [], [], []
        self.conectar()

    def conectar(self) -> None:
        """Engancha el observador del historial y el aviso de fin de evento de la simulación."""
        app = self._app
        app._gestor.historial.observador = self._observar
        if app._simulacion is not None:
            app._simulacion.al_terminar_evento = self.capturar

    def _fijas(self) -> list:
        app = self._app
        j = app._jugador
        estado = app._gestor.estado
        resultado = "victoria" if estado.victoria else "derrota" if estado.derrota else "en curso"
        inventario = app._gestor.inventario
        items = inventario.items() if inventario is not None else []
        return [j.sala, j.vida, j.vida_max, j.ataque, j.defensa, j.velocidad, resultado,
                tuple(f"{it.nombre} (equipado)" if it.equipado else it.nombre for it in items),
                tuple(app._efectos.describir(j))]

    #  Captura

    def _observar(self, etiqueta: str, datos) -> None:
        """Observador del historial: anota los enemigos cuya sala o vida cambia (D4)."""
        if etiqueta != "atributo" or self.linea is None:
            return
        objeto, atributo, anterior = datos
        if (atributo != "sala" and atributo != "vida") or not isinstance(objeto, Enemigo):
            return
        indice = getattr(objeto, "_linea_indice", None)
        if indice is None or indice >= len(self._enemigos) or self._enemigos[indice] is not objeto:
            # Primer cambio: su valor anterior es el que tuvo desde el instante 0.
            sala = anterior if atributo == "sala" else objeto.sala
            vida = anterior if atributo == "vida" else objeto.vida
            indice = len(self._enemigos)
            self._enemigos.append(objeto)
            self._ids.append(objeto.identificador)
            self._ranura_enemigo.append(self.linea.nueva_ranura(sala))
            self.linea.nueva_ranura(vida)
            objeto._linea_indice = indice
            objeto._linea_sucio = False
        if not getattr(objeto, "_linea_sucio", False):
            objeto._linea_sucio = True
            self._sucios.append(objeto)

    def capturar(self, t: int | None = None) -> None:
        """Anexa los cambios del estado observable ocurridos desde la captura anterior."""
        linea = self.linea
        app = self._app
        if linea is None or app._jugador is None:
            return
        if t is None:
            t = app._simulacion.reloj.tiempo_actual
        fijas = self._fijas()
        for ranura in range(len(fijas)):
            linea.registrar(t, ranura, fijas[ranura])
        for enemigo in self._sucios:
            ranura = self._ranura_enemigo[enemigo._linea_indice]
            linea.registrar(t, ranura, enemigo.sala)
            linea.registrar(t, ranura + 1, enemigo.vida)
            enemigo._linea_sucio = False
        self._sucios = []
        registro = app._exploracion.conocimiento.registro
        if self._cursor > len(registro):
            self._cursor = len(registro)
        while self._cursor < len(registro):
            _, tipo, indice, valor = registro[self._cursor]
            base = R_CONOCIMIENTO if tipo == TIPO_ESTADO_SALA else R_CONOCIMIENTO + self._n
            linea.registrar(t, base + indice, valor)
            self._cursor += 1

    def antes_de_accion(self) -> None:
        """Marca la próxima acción del jugador (D5), tras capturar lo pendiente."""
        if self.linea is None:
            return
        t = self._app._simulacion.reloj.tiempo_actual
        self.capturar(t)
        self.linea.marcar(t, self._cursor)

    def _recortar_ultima(self) -> None:
        for enemigo in self._sucios:
            enemigo._linea_sucio = False
        self._sucios = []
        if self.linea.acciones():
            self._cursor = self.linea.recortar(self.linea.acciones())

    def cancelar_accion(self) -> None:
        """La acción falló o lanzó error: su marca y sus cambios desaparecen (FR-008)."""
        if self.linea is not None:
            self._recortar_ultima()

    def tras_pergamino(self) -> None:
        """La acción revertida deja de existir y el descuento del pergamino queda en t (FR-010, FR-011)."""
        if self.linea is None:
            return
        self._recortar_ultima()
        self.capturar()

    #  Consultas

    def historia(self, texto) -> ResultadoHistoria:
        """`historia <t>` o `historia #k` (FR-002 a FR-004). Solo lee."""
        if self.linea is None or self._app._simulacion is None:
            return ResultadoHistoria(False, "No hay una partida en curso.")
        entrada = str(texto).strip()
        if entrada.lower().startswith("historia"):
            entrada = entrada[len("historia"):].strip()
        if entrada.startswith("#"):
            numero = entrada[1:].strip()
            if not numero.isdigit():
                return ResultadoHistoria(False, "Uso: historia #k, con k entero mayor o igual que 1.")
            return self.resumen_en_accion(int(numero))
        if not entrada.isdigit():
            return ResultadoHistoria(False, "Uso: historia <t> o historia #k, con enteros no negativos.")
        return self.resumen_en_tiempo(int(entrada))

    def resumen_hasta(self, t: int) -> ResultadoHistoria:
        """Para `--replay --hasta t`: si t supera el final, el estado final con aviso (FR-022)."""
        if self.linea is None or self._app._simulacion is None:
            return ResultadoHistoria(False, "No hay una partida reproducida.")
        reloj = self._app._simulacion.reloj.tiempo_actual
        if t <= reloj:
            return self.resumen_en_tiempo(t)
        resultado = self.resumen_en_accion(self.linea.acciones() + 1)
        resultado.resumen.aviso = (f"La partida terminó antes del instante {t}: el registro llega "
                                   f"hasta el instante {reloj}.")
        return resultado

    def resumen_en_tiempo(self, t: int, modo: str = CERCANO) -> ResultadoHistoria:
        reloj = self._app._simulacion.reloj.tiempo_actual
        if t > reloj:
            return ResultadoHistoria(False, f"El instante {t} es posterior al reloj actual ({reloj}).")
        pos, marca = self.linea.ubicar_tiempo(t)
        hay_decision = marca >= 0 and self.linea.tiempo_de_accion(marca + 1) == t
        tomadas = marca if hay_decision else marca + 1
        return ResultadoHistoria(True, resumen=self._resumen(pos, marca, t, tomadas, modo))

    def resumen_en_accion(self, numero: int, modo: str = CERCANO) -> ResultadoHistoria:
        n = self.linea.acciones()
        if not 1 <= numero <= n + 1:
            return ResultadoHistoria(False, f"La acción #{numero} no existe: hay {n} acciones, "
                                            f"se puede consultar de #1 a #{n + 1}.")
        pos, marca = self.linea.ubicar_accion(numero)
        reloj = (self.linea.tiempo_de_accion(numero) if numero <= n
                 else self._app._simulacion.reloj.tiempo_actual)
        return ResultadoHistoria(True, resumen=self._resumen(pos, marca, reloj, numero - 1, modo))

    def _resumen(self, pos: int, marca: int, reloj: int, tomadas: int, modo: str) -> ResumenInstante:
        app = self._app
        e = self.linea.estado_en(pos, marca, modo)
        sala_modelo = app._salas.obtener(e[R_SALA])
        resumen = ResumenInstante(
            reloj=reloj, acciones=tomadas, sala_id=e[R_SALA],
            sala_nombre=sala_modelo.nombre if sala_modelo is not None else "?",
            vida=e[R_VIDA], vida_max=e[R_VIDA_MAX], ataque=e[R_ATAQUE], defensa=e[R_DEFENSA],
            velocidad=e[R_VELOCIDAD], resultado=e[R_RESULTADO], inventario=list(e[R_INVENTARIO]),
            efectos=list(e[R_EFECTOS]))
        resumen.enemigos = self._enemigos_en(e, e[R_SALA])
        resumen.mapa = self._mapa(e)
        return resumen

    def _enemigos_en(self, e: list, sala_id: int) -> list[EnemigoInstante]:
        """Enemigos vivos de la sala en ese estado (D4: el que nunca cambió no tiene ranura)."""
        resultado: list[EnemigoInstante] = []
        for indice in range(len(self._enemigos)):
            ranura = self._ranura_enemigo[indice]
            if e[ranura] == sala_id and e[ranura + 1] > 0:
                enemigo = self._enemigos[indice]
                resultado.append(EnemigoInstante(enemigo.identificador, enemigo.nombre,
                                                 e[ranura + 1], enemigo.vida_max))
        sala = self._app._salas.obtener(sala_id)
        if sala is not None:
            for enemigo in sala.enemigos:
                indice = getattr(enemigo, "_linea_indice", None)
                seguido = (indice is not None and indice < len(self._enemigos)
                           and self._enemigos[indice] is enemigo)
                if not seguido and enemigo.vida > 0:
                    resultado.append(EnemigoInstante(enemigo.identificador, enemigo.nombre,
                                                     enemigo.vida, enemigo.vida_max))
        return ordenar(resultado, key=lambda x: x.id)

    def _mapa(self, e: list):
        app = self._app
        vivo = app._exploracion.conocimiento
        if not vivo.inicializado:
            return app._exploracion.mapa_conocido(vivo)
        pasado = ConocimientoJugador()
        pasado.inicializado = True
        pasado._salas = vivo._salas
        pasado._entrantes = vivo._entrantes
        pasado.estado_sala = e[R_CONOCIMIENTO:R_CONOCIMIENTO + self._n]
        pasado.puerta = e[R_CONOCIMIENTO + self._n:R_CONOCIMIENTO + 5 * self._n]
        return app._exploracion.mapa_conocido(pasado)

    #  Persistencia (D9)

    def a_datos(self) -> list:
        nombres = [enemigo.nombre for enemigo in self._enemigos]
        vidas_max = [enemigo.vida_max for enemigo in self._enemigos]
        return [self._n, list(self._ids), nombres, vidas_max, list(self._ranura_enemigo),
                self.linea.a_datos()]

    def restaurar(self, datos: list) -> str | None:
        """Restaura la línea guardada y re-enlaza los enemigos por identificador.

        Devuelve un aviso si `--checkpoint-cada` pedía otro K (FR-027).
        """
        n, ids, nombres, vidas_max, ranuras, linea = datos
        conocimiento = self._app._exploracion.conocimiento
        if n != len(conocimiento.estado_sala):
            raise ValueError("La línea de tiempo no coincide con el esqueleto de la cripta.")
        self.linea = LineaTiempo.desde_datos(linea)
        self._n = n
        self._ids = list(ids)
        self._ranura_enemigo = list(ranuras)
        self._enemigos = [None] * len(ids)
        self._sucios = []
        self._cursor = len(conocimiento.registro)
        for sala_id in range(len(conocimiento.estado_sala)):
            sala = self._app._salas.obtener(sala_id)
            if sala is None:
                continue
            for enemigo in sala.enemigos:
                for indice in range(len(ids)):
                    if ids[indice] == enemigo.identificador:
                        self._enemigos[indice] = enemigo
                        enemigo._linea_indice = indice
                        enemigo._linea_sucio = False
                        break
        for indice in range(len(ids)):
            if self._enemigos[indice] is None:
                # Murió y ya no está en ninguna sala: se conserva su ranura con un sustituto inerte.
                self._enemigos[indice] = _EnemigoAusente(ids[indice], nombres[indice],
                                                         vidas_max[indice])
        self.conectar()
        if self.k_solicitado is not None and self.k_solicitado != self.linea.k:
            return (f"Se ignora --checkpoint-cada {self.k_solicitado}: la partida guardada usa "
                    f"K={self.linea.k}.")
        return None


class _EnemigoAusente:
    """Enemigo de la línea que ya no está en ninguna sala al cargar (por ejemplo, muerto)."""

    def __init__(self, identificador: str, nombre: str, vida_max: int) -> None:
        self.identificador = identificador
        self.nombre = nombre
        self.vida_max = vida_max
        self.vida = 0
