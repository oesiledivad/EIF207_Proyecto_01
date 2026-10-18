"""Heap mínimo propio; cancelación perezosa y deltas de inserción/extracción."""


class Evento:
    __slots__ = ["tiempo_siguiente", "secuencias", "actor", "tipo", "valido", "indice"]

    def __init__(self, tiempo_siguiente: int, secuencias: int, actor, tipo: str):
        self.tiempo_siguiente = tiempo_siguiente
        self.secuencias = secuencias
        self.actor = actor
        self.tipo = tipo
        self.valido = True
        self.indice = -1

    def clave(self):
        return [self.tiempo_siguiente, self.secuencias]


class HeapAgendaEventos:
    def __init__(self, historial=None):
        self._heap: list[Evento] = []
        self._secuencia_actual = 0
        self.historial = historial

    def registrar(self, etiqueta, datos):
        if self.historial is not None:
            self.historial.registrar_si_abierto(etiqueta, datos)

    def cambiar(self, objeto, atributo, valor):
        if self.historial is None:
            setattr(objeto, atributo, valor)
        else:
            self.historial.cambiar(objeto, atributo, valor)
            
    def eventos_validos(self) -> list[Evento]:
        """Eventos pendientes no cancelados (para guardar la partida). O(n), sin orden."""
        return [evento for evento in self._heap if evento.valido]
    
    def peek(self) -> Evento | None:
        """O(1) si la raíz es válida; cada raíz cancelada se extrae en O(log n)."""
        while self._heap and not self._heap[0].valido:
            self._extraer_raiz()
        return self._heap[0] if self._heap else None


    
    

        return [evento for evento in self._heap if evento.valido]
    def insertar(self, tiempo_siguiente: int, actor, tipo: str) -> Evento:
        self.cambiar(self, "_secuencia_actual", self._secuencia_actual + 1)
        evento = Evento(tiempo_siguiente, self._secuencia_actual, actor, tipo)
        self._agregar(evento)
        self.registrar("evento_insertado", [self, evento])
        return evento

    def _agregar(self, evento):
        evento.indice = len(self._heap)
        self._heap.append(evento)
        self._ascender(evento.indice)

    def cancelar(self, evento: Evento) -> None:
        self.cambiar(evento, "valido", False)

    def extraer_siguiente(self) -> Evento | None:
        while self._heap:
            evento = self._extraer_raiz()
            if evento.valido:
                return evento
        return None

    def _extraer_raiz(self):
        evento = self._heap[0]
        self._quitar(evento)
        self.registrar("evento_extraido", [self, evento])
        return evento

    def _quitar(self, evento):
        """El índice del evento evita recorrer el heap al invertir una inserción."""
        i = evento.indice
        if i < 0:
            return
        ultimo = self._heap.pop()
        evento.indice = -1
        if i < len(self._heap):
            self._heap[i] = ultimo
            ultimo.indice = i
            self._ascender(i)
            self._descender(ultimo.indice)

    def _intercambiar(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._heap[i].indice = i
        self._heap[j].indice = j

    @staticmethod
    def _menor(a, b):
        """Compara sin crear listas temporales en cada paso del heap."""
        return (a.tiempo_siguiente < b.tiempo_siguiente
                or a.tiempo_siguiente == b.tiempo_siguiente and a.secuencias < b.secuencias)

    def _ascender(self, i):
        while i > 0:
            padre = (i - 1) // 2
            if not self._menor(self._heap[i], self._heap[padre]):
                break
            self._intercambiar(i, padre)
            i = padre

    def _descender(self, i):
        heap = self._heap
        cantidad = len(heap)
        evento = heap[i]
        while True:
            izq, der = 2 * i + 1, 2 * i + 2
            if izq >= cantidad:
                break
            menor = izq
            if der < cantidad and self._menor(heap[der], heap[izq]):
                menor = der
            if not self._menor(heap[menor], evento):
                break
            # Sube el hijo y deja un hueco: evita intercambiar dos nodos por nivel.
            heap[i] = heap[menor]
            heap[i].indice = i
            i = menor
        heap[i] = evento
        evento.indice = i

    def reprogramar(self, actor, nuevo_tiempo: int, tipo: str) -> Evento:
        """Reemplaza el evento del actor con un único delta reversible."""
        anterior = actor._proximo_evento
        evento = Evento(nuevo_tiempo, self._secuencia_actual + 1, actor, tipo)
        self.registrar("actor_reprogramado", [self, evento, anterior,
                       anterior.valido if anterior is not None else False,
                       actor.tiempo_siguiente, self._secuencia_actual])
        if anterior is not None:
            anterior.valido = False
        self._secuencia_actual += 1
        self._agregar(evento)
        actor._proximo_evento = evento
        actor.tiempo_siguiente = nuevo_tiempo
        return evento
