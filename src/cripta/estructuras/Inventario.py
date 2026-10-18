"""Inventario como lista doble enlazada circular con centinela.

Se eligió lista doble enlazada porque 4.5 exige recorrido bidireccional
y soltar en cualquier posición sin costo dependiente de la posición.
Una `list` con `del lista[i]` sería O(n) al soltar.

El centinela elimina casos especiales al insertar y eliminar. El puntero
`actual` permite recorrer el inventario desde donde está el jugador.

Complejidad:
    agregar: O(1) al frente
    soltar_actual: O(1)
    equipar_actual: O(1)
    siguiente / anterior: O(1)
    vista_ordenada: O(n log n)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from cripta.estructuras.Ordenamientos import ordenar


@dataclass
class ItemInventario:
    """Un objeto dentro del inventario.

    Attributes:
        instancia_id: Identificador único dentro del inventario.
        tipo_id: Identificador de la ficha de catálogo.
        nombre: Nombre legible.
        clase: arma, armadura, pocion, antidoto, llave, antorcha, pergamino_retroceso.
        peso: Peso del objeto.
        valor: Valor del objeto.
        equipado: True si está equipado (arma o armadura).
    """

    instancia_id: str
    tipo_id: str
    nombre: str
    clase: str
    peso: int
    valor: int
    equipado: bool = False
    ataque_bonus: int = 0
    defensa_bonus: int = 0


class _Nodo:
    """Nodo de la lista doble."""

    def __init__(self, item: ItemInventario | None = None) -> None:
        self.item = item
        self.sig: "_Nodo | None" = None
        self.ant: "_Nodo | None" = None


class Inventario:
    """Inventario con recorrido bidireccional.

    Args:
        capacidad: Número máximo de items.
    """

    def __init__(self, capacidad: int = 10) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")
        self._capacidad = capacidad
        self._centinela = _Nodo()
        self._centinela.sig = self._centinela
        self._centinela.ant = self._centinela
        self._tamano = 0
        self._actual: _Nodo | None = None  # None si está vacío

    #  Consultas

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def tamano(self) -> int:
        return self._tamano

    def esta_lleno(self) -> bool:
        return self._tamano >= self._capacidad

    def esta_vacio(self) -> bool:
        return self._tamano == 0

    def item_actual(self) -> ItemInventario | None:
        """Devuelve el item que el jugador está viendo."""
        if self._actual is None:
            return None
        return self._actual.item

    def items(self) -> list[ItemInventario]:
        """Devuelve los items en orden real (frente primero)."""
        resultado: list[ItemInventario] = []
        nodo = self._centinela.sig
        while nodo is not self._centinela:
            if nodo.item is not None:
                resultado.append(nodo.item)
            nodo = nodo.sig
        return resultado

    #  Modificaciones

    def agregar(self, item: ItemInventario) -> bool:
        """Agrega un item al frente. Falla si está lleno.

        Args:
            item: Item a agregar.

        Returns:
            True si se agregó, False si no había espacio.
        """
        if self.esta_lleno():
            return False
        nuevo = _Nodo(item)
        frente = self._centinela.sig
        nuevo.sig = frente
        nuevo.ant = self._centinela
        self._centinela.sig = nuevo
        frente.ant = nuevo
        self._tamano += 1
        if self._actual is None:
            self._actual = nuevo
        return True

    def soltar_actual(self) -> ItemInventario | None:
        """Suelta el item que se está viendo.

        Returns:
            El item soltado, o None si el inventario está vacío.
        """
        if self._actual is None:
            return None
        nodo = self._actual
        item = nodo.item

        # Avanzamos el puntero actual antes de eliminar.
        if self._tamano == 1:
            nuevo_actual = None
        else:
            nuevo_actual = nodo.sig if nodo.sig is not self._centinela else nodo.ant

        # Desenlazamos.
        nodo.ant.sig = nodo.sig
        nodo.sig.ant = nodo.ant
        # El historial puede conservar este nodo como ancla de una extracción.
        self._tamano -= 1
        self._actual = nuevo_actual
        return item

    def soltar_por_id(self, instancia_id: str) -> ItemInventario | None:
        """Suelta un item específico sin mover el puntero actual.

        Args:
            instancia_id: Identificador del item.

        Returns:
            El item soltado, o None si no existe.
        """
        nodo = self._buscar_nodo(instancia_id)
        if nodo is None:
            return None
        item = nodo.item
        if self._actual is nodo:
            if self._tamano == 1:
                self._actual = None
            else:
                self._actual = nodo.sig if nodo.sig is not self._centinela else nodo.ant
        nodo.ant.sig = nodo.sig
        nodo.sig.ant = nodo.ant
        self._tamano -= 1
        return item

    def ancla_actual(self):
        """Predecesor del objeto observado; registrar su extracción cuesta O(1)."""
        return self._actual.ant if self._actual is not None else self._centinela

    def reinsertar_tras(self, item: ItemInventario, ancla) -> bool:
        """Restaura una extracción; omite pergaminos consumidos fuera del historial."""
        if self.esta_lleno():
            return False
        anterior = self._centinela
        while ancla is not self._centinela:
            encontrado = self._buscar_nodo(ancla.item.instancia_id)
            if encontrado is not None:
                anterior = encontrado
                break
            ancla = ancla.ant
        nuevo = _Nodo(item)
        nuevo.ant = anterior
        nuevo.sig = anterior.sig
        anterior.sig.ant = nuevo
        anterior.sig = nuevo
        self._tamano += 1
        if self._actual is None:
            self._actual = nuevo
        return True

    def equipar_actual(self) -> ItemInventario | None:
        """Mueve el item actual al frente y lo marca como equipado.

        Returns:
            El item equipado, o None si el inventario está vacío.
        """
        if self._actual is None:
            return None
        nodo = self._actual
        item = nodo.item
        if item is None:
            return None

        # Si ya está al frente, solo marcamos.
        if nodo.ant is self._centinela:
            item.equipado = True
            return item

        # Desenlazamos y reinsertamos al frente.
        nodo.ant.sig = nodo.sig
        nodo.sig.ant = nodo.ant
        frente = self._centinela.sig
        nodo.sig = frente
        nodo.ant = self._centinela
        self._centinela.sig = nodo
        frente.ant = nodo

        item.equipado = True
        return item

    def equipar_por_id(self, instancia_id: str) -> ItemInventario | None:
        nodo = self._buscar_nodo(instancia_id)
        if nodo is None:
            return None
        anterior = self._actual
        self._actual = nodo
        item = self.equipar_actual()
        self._actual = anterior
        return item

    def seleccionar(self, instancia_id: str) -> ItemInventario | None:
        nodo = self._buscar_nodo(instancia_id)
        if nodo is not None:
            self._actual = nodo
            return nodo.item
        return None

    def desequipar_clase(self, clase: str) -> None:
        """Desmarca como equipado cualquier item de la clase dada.

        Args:
            clase: arma o armadura.
        """
        nodo = self._centinela.sig
        while nodo is not self._centinela:
            if nodo.item is not None and nodo.item.clase == clase and nodo.item.equipado:
                nodo.item.equipado = False
            nodo = nodo.sig

    #  Recorrido

    def siguiente(self) -> ItemInventario | None:
        """Avanza el puntero actual al siguiente item."""
        if self._actual is None:
            return None
        sig = self._actual.sig
        if sig is not self._centinela:
            self._actual = sig
        return self._actual.item

    def anterior(self) -> ItemInventario | None:
        """Retrocede el puntero actual al item anterior."""
        if self._actual is None:
            return None
        ant = self._actual.ant
        if ant is not self._centinela:
            self._actual = ant
        return self._actual.item

    def ir_al_frente(self) -> ItemInventario | None:
        """Coloca el puntero actual en el primer item."""
        if self._tamano == 0:
            return None
        self._actual = self._centinela.sig
        return self._actual.item

    #  Búsqueda

    def buscar_por_id(self, instancia_id: str) -> ItemInventario | None:
        """Busca un item por su identificador de instancia."""
        nodo = self._buscar_nodo(instancia_id)
        return nodo.item if nodo is not None else None

    def _buscar_nodo(self, instancia_id: str) -> _Nodo | None:
        nodo = self._centinela.sig
        while nodo is not self._centinela:
            if nodo.item is not None and nodo.item.instancia_id == instancia_id:
                return nodo
            nodo = nodo.sig
        return None

    #  Vistas ordenadas

    def reinsertar_en(self, item: ItemInventario, posicion: int) -> bool:
        """Reinserta un item en una posición relativa al frente.

        Se usa al deshacer: restaura un item quitado en el lugar donde
        estaba para que el orden real no cambie.

        Args:
            item: Item a reinsertar.
            posicion: Posición relativa al frente (0 = primero).

        Returns:
            True si se reinsertó, False si no había espacio.
        """
        if self.esta_lleno():
            return False

        nuevo = _Nodo(item)
        actual = self._centinela.sig
        for _ in range(max(0, posicion)):
            if actual is self._centinela:
                break
            actual = actual.sig
        nuevo.sig = actual
        nuevo.ant = actual.ant
        actual.ant.sig = nuevo
        actual.ant = nuevo

        self._tamano += 1
        if self._actual is None:
            self._actual = nuevo
        return True

    def posicion_de(self, instancia_id: str) -> int | None:
        """Devuelve la posición relativa al frente, o None si no existe."""
        nodo = self._centinela.sig
        i = 0
        while nodo is not self._centinela:
            if nodo.item is not None and nodo.item.instancia_id == instancia_id:
                return i
            nodo = nodo.sig
            i += 1
        return None

    def vista_ordenada(self, clave: Callable[[ItemInventario], object]) -> list[ItemInventario]:
        """Devuelve una vista ordenada sin alterar el orden real.

        Args:
            clave: Función que extrae el campo de ordenamiento.

        Returns:
            Nueva lista ordenada con referencias a los mismos items.
        """
        copia = self.items()
        return ordenar(copia, key=clave)

    def vista_por_peso(self) -> list[ItemInventario]:
        return self.vista_ordenada(lambda i: i.peso)

    def vista_por_valor(self) -> list[ItemInventario]:
        return self.vista_ordenada(lambda i: i.valor)

    def vista_por_nombre(self) -> list[ItemInventario]:
        return self.vista_ordenada(lambda i: i.nombre)
