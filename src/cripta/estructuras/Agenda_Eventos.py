"""
    src/cripta/estructuras/agenda_eventos.py

    Este módulo contiene las estructuras necesarias para manejar
    la agenda de eventos de la simulación mediante un heap mínimo.
"""

class Evento:
    """
        Clase que representa un evento en la agenda de eventos.
        El evento tiene un tiempo de ejecución, una secuencia de inserción,
        un actor al que corresponde y un tipo de evento.
    """
    def __init__(self, tiempo_siguiente: int, secuencias: int, actor, tipo: str ):
        self.tiempo_siguiente = tiempo_siguiente
        self.secuencias = secuencias
        self.actor = actor # a quien pertenece el evento, jugador o enemigo
        self.tipo = tipo   # ej: "accion_actor", "veneno", "cierre_puerta"
        self.valido = True

    def clave(self):
        """
              Devuelve la clave utilizada para ordenar los eventos.

              Los eventos se ordenan primero por tiempo y luego por
              número de secuencia.
        """
        return self.tiempo_siguiente, self.secuencias

class HeapAgendaEventos:
    """
       Administra los eventos de la simulación mediante un heap mínimo.

       Permite insertar, extraer, cancelar y reprogramar eventos.
       La cancelación se realiza de forma perezosa, marcando el evento
       como inválido sin eliminarlo inmediatamente del heap.
    """
    def __init__(self):
        self._heap: list[Evento] = []
        self._secuencia_actual = 0

    def peek(self) -> Evento | None:
        """Devuelve el evento con menor clave sin extraerlo. O(1) amortizado."""
        while self._heap and not self._heap[0].valido:
            self._extraer_raiz()  # descarta basura que quedó en la raíz
        return self._heap[0] if self._heap else None

    # O(1) solo incrementa un contador
    def _siguiente_secuencia(self) -> int:
        self._secuencia_actual += 1
        return self._secuencia_actual

    # O(log n) agrega al final y hace ascender()
    def insertar(self, tiempo_siguiente: int, actor, tipo: str) -> Evento:
        evento = Evento(tiempo_siguiente, self._siguiente_secuencia(), actor, tipo)
        self._heap.append(evento)
        self._ascender(len(self._heap) - 1)
        return evento

    # O(1) no se toca el arreglo
    def cancelar(self, evento: Evento) -> None:
        evento.valido = False

    # O(log n)
    def extraer_siguiente(self) -> Evento | None:
        while self._heap:
            candidato = self._extraer_raiz()
            if candidato.valido:
                return candidato
            # si era basura, seguimos extrayendo hasta encontrar uno válido
        return None

    # O(log n) extrae la raiz y hace descender()
    def _extraer_raiz(self) -> Evento:
        raiz = self._heap[0]
        ultimo = self._heap.pop()
        if self._heap:
            self._heap[0] = ultimo
            self._descender(0)
        return raiz

    # O(log n) asciende el elemento en la posicion i hasta que cumpla la propiedad de heap
    def _ascender(self, i: int) -> None:
         # Esta funcion asciende el elemento en la posicion i hasta que cumpla la propiedad de heap
         while i > 0:
             padre = (i - 1) // 2

             if self._heap[i].clave() < self._heap[padre].clave():
                    self._heap[i], self._heap[padre] = self._heap[padre], self._heap[i]
                    i = padre
             else:
                 break

    # O(log n) baja el elemento en la posicion i hasta que cumpla la propiedad de heap
    def _descender(self, i: int) -> None:
        # bajar hacia el menor mientras rompa la propiedad de heap
        while True:
            izq = 2 * i + 1
            der = 2 * i + 2
            menor = i
            if izq < len(self._heap) and self._heap[izq].clave() < self._heap[menor].clave():
                menor = izq
            if der < len(self._heap) and self._heap[der].clave() < self._heap[menor].clave():
                menor = der
            if menor == i:
                break
            self._heap[i], self._heap[menor] = self._heap[menor], self._heap[i]
            i = menor

    # O(log n) cancela en O(1) e inserta en O(log n)
    def reprogramar(self, actor, nuevo_tiempo: int, tipo: str) -> Evento:
        if actor._proximo_evento is not None:
            self.cancelar(actor._proximo_evento)
        nuevo_evento = self.insertar(nuevo_tiempo, actor, tipo)
        actor._proximo_evento = nuevo_evento
        return nuevo_evento
