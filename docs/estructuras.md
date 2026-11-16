# Estructuras de datos

Operaciones del código actual; las alternativas y mediciones están en [decisiones.md](decisiones.md). `list` se utiliza como almacenamiento de bajo nivel, no se emplea `dict` como índice propio.

Notación: $n$ objetos, $k$ deltas, $c$ capacidad de caché, $p$ puntajes, $a$ acciones y $s$ salas del archivo.

## 1. Inventario: lista doble circular (§4.5)

Cada nodo guarda un objeto y enlaces `ant` y `sig`. Un centinela conecta los extremos; el cursor identifica el seleccionado. La capacidad viene de `inventario_max`.

| Operación de la estructura                                  | Costo                         |
|-------------------------------------------------------------|-------------------------------|
| Agregar al frente; consultar tamaño                         | $O(1)$                        |
| Siguiente/anterior; soltar o mover al frente el nodo actual | $O(1)$                        |
| Buscar o seleccionar por ID; recorrer objetos               | $O(n)$                        |
| Vista ordenada                                              | Copia $O(n)$ más ordenamiento |

**Invariantes:** capacidad respetada, enlaces recíprocos y cursor válido o `None`. El recorrido se detiene en los extremos; ordenar una vista conserva el orden real.

Equipar puede buscar y desmarcar otro objeto: la acción completa no es constante. Soltar registra un ancla en $O(1)$; restaurarla puede buscar nodos y omitir pergaminos consumidos.

Código: [Inventario.py](../src/cripta/estructuras/Inventario.py).

## 2. Historial: pila acotada de deltas (§4.6)

Una acción abre un intervalo de `Cambio(etiqueta, datos)`; deshacer aplica sus inversas desde el último cambio. Se conservan cinco intervalos, sin instantáneas del mundo.

- Registrar: $O(1)$ amortizado.
- Cerrar: al descartar el más antiguo desplaza como máximo cinco referencias.
- Deshacer: recorrido $O(k)$ más las inversas; buscar objetos y modificar el heap añaden su costo.
- Memoria: $O(\sum\limits_{i=1}^{h} k_i)$ cambios, con $h\leq5$; $k_i$ cuenta los cambios del intervalo $i$. No es constante en bytes.

**Invariantes:** un solo intervalo abierto, azar restaurable y pergaminos consumidos fuera del retroceso. La agenda registra la reprogramación como un delta compuesto.

Código: [Historial_Retroceso.py](../src/cripta/estructuras/Historial_Retroceso.py) y [GestorPartida.py](../src/cripta/controlador/GestorPartida.py).

## 3. Ordenamientos propios (§4.9)

| Algoritmo estable | Tiempo                      | Memoria auxiliar |
|-------------------|-----------------------------|------------------|
| Inserción         | Mejor $O(n)$; peor $O(n^2)$ | $O(1)$           |
| Mezcla            | $O(n\log n)$                | $O(n)$           |

El selector usa inserción para $n\leq16$ o menos de 10 % de descensos en la muestra; en otro caso, mezcla. Puede clasificar mal: su peor caso sigue siendo cuadrático. Las claves se recalculan en las comparaciones.

Se reutilizan en inventario, puntajes, índices y listas auxiliares, sin `sorted()` ni `list.sort()`.

Código: [Ordenamientos.py](../src/cripta/estructuras/Ordenamientos.py).

## 4. Puntajes: lista de registros

`Puntaje` conserva identidad, jugador, cripta/versión, resultado, acciones, enemigos derrotados y tiempo. `TablaPuntajes` evita duplicados por ID y reemplaza el JSON atómicamente.

Registrar cuesta $O(p)$ por lectura, comprobación y escritura. Ordenar usa los algoritmos anteriores; no se calcula una puntuación numérica adicional.

Código: [Puntajes.py](../src/cripta/adaptadores/Puntajes.py).

## 5. Replay: registro secuencial (§4.11)

Cabecera: formato, cripta/catálogo y versiones, semilla, jugador y capacidad de caché. Después se anexan acciones y argumentos. El reproductor lee $a$ acciones en memoria y las ejecuta mediante el controlador, sin ventana.

**Invariantes:** acciones válidas, versiones compatibles y secuencia reproducible de llamadas al azar. Reproducir el log no equivale a continuar un guardado.

Código: [reproductor.py](../src/cripta/replay/reproductor.py).

## 6. Estructuras compartidas: integración

- **Caché LRU:** lista doble propia; buscar/desalojar, $O(c)$; mover nodo conocido, $O(1)$. Las fichas referenciadas están protegidas.
- **Agenda:** heap propio que organiza los eventos de combate y efectos; sus cambios se registran para permitir el retroceso.
- **Guardado:** cabecera, índice de IDs/offsets y cuerpos; permite restaurar partidas desde el menú y consultar salas individuales.

`cargar_sala` relee y recorre el índice en cada llamada: $O(s+b)$ para devolver $b$ bytes, sin leer los cuerpos de las otras salas. No es acceso $O(1)$.

Código: [Cache_Fichas.py](../src/cripta/estructuras/Cache_Fichas.py), [Agenda_Eventos.py](../src/cripta/estructuras/Agenda_Eventos.py) y [Guardado_Binario.py](../src/cripta/estructuras/Guardado_Binario.py).

## 7. Resolubilidad: cola con índice de cabeza e índice de llaves (§3.5, §5.4)

Notación: $n$ elementos de la cola, $K$ llaves distintas, $m$ ids que se indexan (salidas cerradas y ubicaciones). Las razones de elegirlas y su comparación medida están en la [sección 12 de decisiones.md](decisiones.md#12-resolubilidad-de-la-cripta-parte-ii-35-y-54).

### `ColaLista`: cola FIFO

Una `list` y un índice de cabeza. Sacar avanza el índice y suelta la referencia sin desplazar la lista; no usa `list.pop(0)` ni `deque`.

| Operación                           | Costo                   |
|-------------------------------------|-------------------------|
| `encolar`                           | $O(1)$ amortizado       |
| `sacar`                             | $O(1)$                  |
| `vacia`                             | $O(1)$                  |

**Invariantes:** el orden de salida es el de entrada; sacar de una cola vacía lanza `IndexError`. La lista conserva las posiciones ya sacadas hasta que la cola se descarta, así que ocupa $O(n)$ de memoria por todas las inserciones y no se reutiliza entre rondas.

### `IndiceLlaves`: arreglo ordenado con búsqueda binaria

Guarda los ids de llave distintos, ordenados con `ordenar` del proyecto. El rango de una llave es su posición, de modo que «menor id» equivale a «menor rango». No usa `dict`, `set` ni `bisect`.

| Operación                     | Costo                                              |
|-------------------------------|----------------------------------------------------|
| Construcción                  | $O(m\log m)$: ordenar y quitar repetidos           |
| `rango` (id a posición)       | $O(\log K)$ por búsqueda binaria; $-1$ si no existe |
| `cantidad`                    | $O(1)$                                             |
| `ids` (copia en orden)        | $O(K)$                                             |

**Invariantes:** ids distintos y en orden lexicográfico; el resultado no depende del orden de la entrada. Este índice es el factor $\log K$ de la verificación, que por lo demás cuesta $O(S+E+K)$. La medición M4 lo comparó con una tabla hash propia y conserva el arreglo.

Código: [Cola_Lista.py](../src/cripta/estructuras/Cola_Lista.py) e [Indice_Llaves.py](../src/cripta/estructuras/Indice_Llaves.py).
