"""
    src/cripta/estructuras/agenda_eventos.py
    Este modulo es para la estructura de datos que usaremos para manejar
    nuestra agenda de eventos implementada con un heap.
"""

class Evento:
    def __init__(self, tiempo_siguiente: int, secuencias: int, actor, tipo: str ):
        self.tiempo_siguiente = tiempo_siguiente
        self.secuencias = secuencias
        self.actor = actor # a quien pertenece el evento, jugador o enemigo
        self.tipo = tipo   # ej: "accion_actor", "veneno", "cierre_puerta"
        self.valido = True

    def clave(self):
        return self.tiempo_siguiente, self.secuencias

class AgendaEventos:
    def __init__(self):
        self._heap: list[Evento] = []
        self._secuencia_actual = 0

    def _siguiente_secuencia(self) -> int:
        self._secuencia_actual += 1
        return self._secuencia_actual

    def insertar(self, tiempo_siguiente: int, actor, tipo: str) -> Evento:
        evento = Evento(tiempo_siguiente, self._siguiente_secuencia(), actor, tipo)
        self._heap.append(evento)
        self._ascender(len(self._heap) - 1)
        return evento

    def cancelar(self, evento: Evento) -> None:
        evento.valido = False # O(1) no se toca el arreglo

    def extraer_siguiente(self) -> Evento | None:
        while self._heap:
            candidato = self._extraer_raiz()
            if candidato.valido:
                return candidato
            # si era basura, seguimos extrayendo hasta encontrar uno válido
        return None

    def _extraer_raiz(self) -> Evento:
        raiz = self._heap[0]
        ultimo = self._heap.pop()
        if self._heap:
            self._heap[0] = ultimo
            self._descender(0)
        return raiz

    def _ascender(self, i: int) -> None:
         # Esta funcion asciende el elemento en la posicion i hasta que cumpla la propiedad de heap
         while i > 0:
             padre = (i - 1) // 2

             if self._heap[i].clave() < self._heap[padre].clave():
                    self._heap[i], self._heap[padre] = self._heap[padre], self._heap[i]
                    i = padre
             else:
                 break

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

    def reprogramar(self, actor, nuevo_tiempo: int, tipo: str) -> Evento:
        # cancela el evento viejo sin tocarlo e inserta uno nuevo con el tiempo actualizado
        self.cancelar(actor._proximo_evento)
        nuevo_evento = self.insertar(nuevo_tiempo, actor, tipo)
        actor._proximo_evento = nuevo_evento

        return nuevo_evento
