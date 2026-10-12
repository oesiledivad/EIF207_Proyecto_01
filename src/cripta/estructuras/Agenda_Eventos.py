"""Heap mínimo propio; cancelación perezosa y deltas de inserción/extracción."""


class Evento:
    def __init__(self, tiempo_siguiente: int, secuencias: int, actor, tipo: str):
        self.tiempo_siguiente = tiempo_siguiente
        self.secuencias = secuencias
        self.actor = actor
        self.tipo = tipo
        self.valido = True
        self.indice = -1

    def clave(self):
        return self.tiempo_siguiente, self.secuencias


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
        self.registrar("evento_insertado", (self, evento))
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
        self.registrar("evento_extraido", (self, evento))
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

    def _ascender(self, i):
        while i > 0:
            padre = (i - 1) // 2
            if self._heap[i].clave() >= self._heap[padre].clave():
                break
            self._intercambiar(i, padre)
            i = padre

    def _descender(self, i):
        while True:
            menor = i
            izq, der = 2 * i + 1, 2 * i + 2
            if izq < len(self._heap) and self._heap[izq].clave() < self._heap[menor].clave():
                menor = izq
            if der < len(self._heap) and self._heap[der].clave() < self._heap[menor].clave():
                menor = der
            if menor == i:
                return
            self._intercambiar(i, menor)
            i = menor

    def reprogramar(self, actor, nuevo_tiempo: int, tipo: str) -> Evento:
        if actor._proximo_evento is not None:
            self.cancelar(actor._proximo_evento)
        evento = self.insertar(nuevo_tiempo, actor, tipo)
        self.cambiar(actor, "_proximo_evento", evento)
        self.cambiar(actor, "tiempo_siguiente", nuevo_tiempo)
        return evento
