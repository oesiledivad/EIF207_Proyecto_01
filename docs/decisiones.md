# Decisiones de diseño

EIF 207 · Estructuras de Datos.

Este documento reúne las decisiones de diseño, sus costos y limitaciones. El detalle de operaciones está en [estructuras.md](estructuras.md).

## 1. Agenda de eventos (§4.1)

**Necesidad y elección.** Obtener el próximo evento, cancelar acciones y reprogramarlas cuando cambia la velocidad. Elegimos un heap mínimo propio, ordenado por tiempo y secuencia, con invalidación perezosa: cancelar marca el evento como inválido y reprogramar inserta su reemplazo.

**Alternativas.** Una lista ordenada requiere $O(n)$ por inserción. El heap permite insertar en $O(\log n)$ y cancelar en $O(1)$. La eliminación inmediata también es posible usando el índice del evento, pero se conserva la marca para registrar una cancelación como un único cambio reversible.

**Costo y límite.** Cada extracción física cuesta $O(\log n)$. Consultar una raíz válida cuesta $O(1)$; descartar $r$ raíces inválidas cuesta $O(r\log n)$. Las cancelaciones pueden acumular eventos inválidos: una referencia activa por actor no limita esa acumulación.

### Comparación medida

| $n$ eventos | Heap: insertar | Heap: extraer | Lista: insertar | Lista: extraer |
|-------------|---------------:|--------------:|----------------:|---------------:|
| 100         |        0,11 ms |       0,18 ms |         0,18 ms |        0,01 ms |
| 500         |        0,53 ms |       1,15 ms |         4,17 ms |        0,07 ms |
| 2000        |        2,46 ms |       6,00 ms |        79,06 ms |        0,35 ms |

**Reproducción:** `uv run cripta --bench`, sección «Agenda», implementada en
[src/cripta/bench.py](../src/cripta/bench.py). Ejecución en el entorno de §11; una muestra por tamaño. Ambos reciben los mismos tiempos
pseudoaleatorios, con `random.Random(42)`. Se mide primero insertar los $n$
eventos y después vaciar la estructura, sin cancelaciones ni historial.

A $n=2000$, insertar y extraer todo suma $8{,}46\,\mathrm{ms}$ para el heap y
$79{,}41\,\mathrm{ms}$ para la lista. La lista gana en extracción aislada, pero
pierde en la carga combinada medida. Mantenerla ordenada exige desplazar y
comparar elementos: $n$ inserciones cuestan $O(n^2)$ en el peor caso, frente a
$O(n\log n)$ del heap. Esto apoya elegir el heap para inserciones y extracciones
repetidas; no demuestra una ventaja en todas las cargas ni mide la invalidación.
Los tiempos también incluyen diferencias de representación: el heap crea eventos
y actores de prueba; la alternativa almacena pares de tiempo y secuencia.

## 2. Combate e IA de enemigos (§2.6, §2.8)

**Necesidad y elección.** Compartir la regla de atacar al jugador presente y separar el movimiento de `Guardian`, `Errante` y `Rastreador`. `Enemigo.decidir_accion` resuelve lo común y delega en `_decidir_movimiento`; `match/case` selecciona la clase del catálogo. El combate usa `random.Random(semilla)` para poder reproducirse.

**Alternativas.** Un método con todos los comportamientos mezcla reglas independientes; una tabla de despacho con `dict` incumple la restricción de usarlo como estructura de resolución. La herencia permite compartir la decisión común sin repetirla.

**Costo.** Guardián y Errante tienen costo $O(1)$ con hasta cuatro salidas. Rastreador consulta $k$ vecinos y ordena candidatos: $O(k^2)$ con inserción para $k\leq4$. Con esa cota, no depende del total de salas.

### Comparación medida

| Salas | 10 000 llamadas a `decidir_accion` | Por llamada |
|-------|-----------------------------------:|------------:|
| 20    |                            6,16 ms |    0,616 µs |
| 200   |                            6,16 ms |    0,616 µs |
| 2000  |                            6,22 ms |    0,622 µs |

**Reproducción:** `uv run cripta --bench`, sección «Rastreador.decidir_accion»,
en [src/cripta/bench.py](../src/cripta/bench.py). Entorno de §11;
una muestra por tamaño, cripta lineal y `random.Random(1)`. La construcción de
la cripta queda fuera del tiempo. Cada llamada consulta la sala central y sus
salidas; no hay rastro vigente, por lo que se mide la decisión de esperar.

Aumentar las salas $100$ veces cambia el tiempo total de $6{,}16$ a
$6{,}22\,\mathrm{ms}$. Es compatible con consultar solo vecinos mediante el
índice directo, en lugar de recorrer toda la cripta. No compara herencia contra
otras formas de despacho ni mide la ordenación de candidatos con rastro vigente.

**Límite.** El daño mínimo de una unidad puede alargar combates entre actores con defensa alta respecto al ataque.

## 3. Efectos temporales (§2.10)

**Necesidad y elección.** Veneno, regeneración y cambios de velocidad deben coexistir y cancelarse sin interrumpir la acción del actor. Cada efecto usa eventos independientes en la agenda existente; al morir, se cancelan sus referencias pendientes.

**Alternativa.** Revisar todos los efectos en un tick fijo introduce consultas periódicas aunque ninguno deba actuar. Los eventos independientes aprovechan el reloj virtual y el mecanismo de cancelación ya implementado.

**Evidencia y costo.** Se reutiliza `HeapAgendaEventos`, cuya inserción y extracción física cuestan $O(\log n)$ (§1). Esto justifica compartir la estructura; no mide el costo completo de los efectos ni compara experimentalmente ambas estrategias.

**Límite.** Cada efecto añade trabajo a la agenda. Volver a aplicar veneno reinicia su duración de 400 unidades —cinco pulsos de 80— en lugar de acumularla.

## 4. Caché de catálogo (§4.3–§4.4, integración)

- **Problema:** reutilizar fichas sin exceder `--cache-size` ni desalojar las que están en uso.
- **Alternativas:** `dict` y tabla hash propia se descartan por las restricciones del proyecto y de clase; se conserva una lista doble LRU propia.
- **Decisión:** buscar por clave en la lista, mover los aciertos al frente y desalojar desde la cola una ficha sin referencias. Se consulta disco antes de pedir fichas a la red. `CatalogoService` resuelve y protege; `PrecargaService` organiza lotes.
- **Costo:** buscar o desalojar cuesta $O(c)$ para capacidad $c$; mover un nodo conocido cuesta $O(1)$. Deduplicar $k$ identificadores cuesta $O(k^2)$.
- **Evidencia:** con 25 fichas, 50 000 aciertos tomaron 10,33 ms y 50 000 fallos, 55,70 ms en la ejecución de §11. Esto no demuestra búsqueda constante para otras capacidades.
- **Límite:** si las fichas protegidas superan la capacidad, se rechaza la operación y se solicita aumentar `--cache-size`. Una cripta local usa su catálogo local; no se mezclan versiones con la caché online.

## 5. Inventario (§4.5)

- **Problema:** recorrer en ambas direcciones y soltar el seleccionado sin depender de su posición.
- **Alternativas:** una lista contigua desplaza hasta $n-1$ referencias al borrar; una lista simple debe recorrer nodos para encontrar el anterior.
- **Decisión:** lista doble circular con centinela y cursor. Las vistas ordenan una copia; soltar registra objeto y ancla.
- **Costo:** operaciones sobre el nodo actual, $O(1)$; búsqueda por ID y comprobación del equipo anterior, $O(n)$.
- **Evidencia:** 10 000 pares agregar/soltar: 4,058 ms; siguiente/anterior: 2,051 ms (§11). `test_soltar_actual_no_busca_por_id_ni_posicion` comprueba que soltar no realiza búsquedas.
- **Límite:** seleccionar por ID requiere búsqueda previa; equipar y deshacer no son necesariamente constantes.

## 6. Retroceso (§4.6)

- **Problema:** deshacer cinco acciones y sus eventos sin copiar el mundo ni recuperar pergaminos.
- **Alternativas:** instantáneas completas, prohibidas; registro ilimitado, con crecimiento de memoria.
- **Decisión:** intervalos acotados de deltas, aplicados en orden inverso. Se restaura el azar; los pergaminos quedan fuera del retroceso. Reprogramar un actor usa un delta compuesto.
- **Costo:** registrar, $O(1)$ amortizado; recorrer $k$ cambios, $O(k)$, más sus inversas. Algunas buscan objetos o modifican el heap.
- **Evidencia:** 10 000 intervalos registrando y revirtiendo diez atributos: 60,664 ms. `test_retroceso` contrasta reloj, azar, agenda, inventario y puertas; también verifica el límite de cinco intervalos.
- **Límite:** cinco intervalos no significan memoria constante en bytes. El historial no se conserva al cargar.

## 7. Ordenamientos (§4.9)

- **Problema:** ordenar inventario, puntajes e índices sin `sorted()` ni `list.sort()`.
- **Alternativas:** siempre inserción penaliza datos desordenados grandes; siempre mezcla añade trabajo en listas pequeñas.
- **Decisión:** algoritmos propios y estables. Se usa inserción si $n\leq16$ o el muestreo tiene menos de 10 % de descensos; en otro caso, mezcla. El paso de muestra es $\max(1,\lfloor n/64\rfloor)$.
- **Costo:** inserción, $O(n^2)$ peor caso y $O(n)$ mejor; mezcla, $O(n\log n)$ y memoria $O(n)$.
- **Evidencia:** medias de tres repeticiones; incluyen copiar, ordenar y comprobar el resultado.

| Datos                            | Inserción |   Mezcla |
|----------------------------------|----------:|---------:|
| 16 aleatorios, clave simple      |  0,014 ms | 0,022 ms |
| 512 aleatorios, clave simple     |  6,199 ms | 1,162 ms |
| 512 casi ordenados, clave simple |  0,117 ms | 0,764 ms |
| 512 aleatorios, clave costosa    | 55,423 ms | 6,834 ms |

**Límite:** el muestreo puede equivocarse; el selector no garantiza $O(n\log n)$ ni el algoritmo más rápido. Las claves se recalculan durante las comparaciones.

## 8. Cierre y puntajes

- **Problema:** registrar victoria, derrota o abandono una sola vez.
- **Alternativas:** guardar al dibujar puede duplicar resultados; una base de datos añade complejidad para una tabla local; un árbol ordenado tampoco evita reescribir el JSON completo.
- **Decisión:** `PartidaControlador` comprueba el final; `TablaPuntajes` evita duplicados por ID y reemplaza el JSON atómicamente. Prioridad: victoria, más enemigos derrotados, menos acciones, menor tiempo, nombre e ID.
- **Costo:** registrar $p$ resultados cuesta $O(p)$; ordenar depende de §7.
- **Evidencia:** `test_partida` y `test_puntajes` verifican salida, cierre y duplicados; no son mediciones temporales.
- **Límite:** se lee y reescribe toda la tabla. Cheats deshabilita puntajes normales.

## 9. Registro y replay (§4.11)

- **Problema:** reproducir acciones con iguales datos, semilla y secuencia de llamadas al azar.
- **Alternativas:** estados completos por acción ocupan más; los mensajes visuales no reconstruyen las acciones.
- **Decisión:** texto de solo anexado: cabecera de versiones y semilla, seguida de acciones y argumentos. Reutiliza el controlador sin ventana.
- **Costo:** anexar depende de la longitud de la línea; leer $a$ acciones usa $O(a)$ registros, además de ejecutarlas.
- **Evidencia:** `test_replay` y `test_stormlight` contrastan el estado y la agenda reproducidos.
- **Límite:** carga todo el log, exige versiones compatibles y no sustituye al guardado para continuar jugando.

## 10. Integración y vista

Se descartó concentrar interfaz, red y reglas en `Aplicacion`: ahora delega en controladores y servicios. El ciclo coordina tiempo, historial y registro; Arcade presenta el estado sin que las animaciones adelanten el reloj. `bootstrap` permite ejecutar `--replay` y `--bench` sin ventana.

Un error de red permite reintentar, volver o salir. Agotar el presupuesto no termina la partida: permite datos disponibles, rechaza descargas sin consumir una acción y ofrece guardar. Reintentar no renueva el presupuesto ni cambia automáticamente a offline.

### Registros y frontera con la API

Usamos `dataclass` para declarar campos con nombre y valores predeterminados sin repetir constructores. Frente a clases manuales, evita mantener asignaciones repetidas; frente a listas posicionales, permite leer `ficha.ataque` sin recordar un índice. La biblioteca estándar genera `__init__`, `__repr__` y comparación por campos.

El flujo de fichas es:

**JSON de red o disco → `parsear_ficha` → ficha `dataclass` → catálogo en memoria → juego.**

[CatalogoService](../src/cripta/servicio/CatalogoService.py) llama a [parsear_ficha](../src/cripta/dto/FactoryDto_Ficha.py), que selecciona `FichaEnemigo`, `FichaArma` u otra clase según `clase`. [FactoryDto_Partida.py](../src/cripta/dto/FactoryDto_Partida.py) convierte detalles y salas, aplicando valores predeterminados. Los datos crudos quedan en la frontera de transporte y pueden persistirse en disco; el catálogo de juego recibe fichas, tanto en red como en offline.

**Evidencia.** [FichaEnemigo](../src/cripta/dto/EnemigoDto.py) hereda los campos de `FichaCatalogo` sin repetir un constructor; [ResultadoAccion](../src/cripta/dto/ResultadoAccion.py) declara `motivo=""` y `datos=None`. [Puntaje](../src/cripta/adaptadores/Puntajes.py) mantiene validación en `__post_init__` y usa `asdict` para preparar el JSON.

**Límites.** El parser rechaza clases desconocidas y el constructor rechaza campos obligatorios ausentes o argumentos no declarados. `dataclass` no valida tipos ni rangos, no hace inmutables los objetos por defecto y no reduce solicitudes HTTP. Con $f$ campos escalares realiza $O(f)$ asignaciones, igual que un constructor manual: su beneficio es la claridad y el mantenimiento.

## 11. Mediciones y límites

**Entorno:** Windows x64, Python 3.13.16; CPU identificada como Intel64 Family 6 Model 158 Stepping 10. Reproducción:

```sh
uv run cripta --bench
```

Semilla 42 para cargas aleatorias, salvo la prueba de decisión del rastreador, que usa 1. Los resultados corresponden a una ejecución. Los ciclos incluyen historial y actualización del estado, excluyendo red, disco y renderizado.

| Ciclo completo                               | Muestras |     Media |    Máximo |
|----------------------------------------------|---------:|----------:|----------:|
| Referencia `cripta-01`, movimiento y combate |       61 |  0,141 ms |  0,986 ms |
| Sintético, 20 enemigos                       |      100 |  0,258 ms |  1,038 ms |
| Sintético, 200 enemigos                      |      100 |  2,606 ms |  4,594 ms |
| Sintético, 500 enemigos                      |      100 |  7,514 ms | 20,335 ms |
| Sintético, 1000 enemigos                     |      100 | 16,085 ms | 42,496 ms |

La referencia medida cumple $T<20\,\mathrm{ms}$; 500 y 1000 enemigos presentan picos superiores. No prueba todas las criptas. Influyen equipo, implementación, eventos y recolección de memoria, no solo las restricciones académicas.

### Guardado: acceso selectivo frente a JSON completo

El índice binario permite consultar una sala sin leer los cuerpos restantes. La alternativa, un único documento JSON, requiere leerlo y decodificarlo completo. El índice actual se recorre en $O(s)$; no ofrece acceso constante.

**Carga medida:** cien salas sintéticas, diez repeticiones. El benchmark coloca JSON por sala dentro del contenedor binario; no representa una partida completa.

| Medida             |  Binario |     JSON |
|--------------------|---------:|---------:|
| Tamaño             | 41 917 B | 40 903 B |
| Guardar, media     | 0,484 ms | 1,009 ms |
| Cargar todo, media | 1,549 ms | 0,840 ms |

Leer una sala binaria promedió **0,192 ms**. El acceso selectivo es su ventaja; no resultó menor ni más rápido cargando todo.

## 12. Resolubilidad de la cripta (Parte II, §3.5 y §5.4)

**Necesidad y elección.** Decidir, antes de jugar y sin red durante la decisión, si la cripta se puede ganar, en qué orden se obtienen las llaves y, si no se puede, por qué. El modelo (`modelo/Resolubilidad.py`) recibe el esqueleto de salas y la ubicación publicada de las llaves; no conoce HTTP, archivos ni vista. Elegimos una única exploración en anchura por rondas con una lista de espera por llave (D1 y D2 de [research.md](../specs/001-resolubilidad/research.md)). Cada salida cerrada cuya llave aún no se tiene queda en la espera de esa llave; al obtener la llave se liberan sus salidas. La exploración no se detiene al ganar, porque la spec exige todas las llaves obtenibles (FR-007).

**Orden determinista.** La exploración avanza por rondas y cada ronda se ordena por id de sala con `ordenar` del proyecto. Las salidas de una sala se recorren por (destino, dirección) y las llaves de una sala por id. Con ello una llave publicada en varias salas se obtiene en la alcanzable primero y, en empate de ronda, en la de menor id (FR-008). Dos ejecuciones con los mismos datos dan el mismo orden.

**Alternativas descartadas.**

| Alternativa | Costo | Motivo |
|-------------|-------|--------|
| Repetir la exploración completa cada vez que se obtiene una llave | $O(K\,(S+E))$ | Es la que FR-024 prohíbe. Solo vive en `--bench` como contraste (M1) |
| Iterar hasta punto fijo sobre todas las puertas | $O(K\,E)$ en el peor caso | Misma familia que la anterior, sin mejora de cota |
| Búsqueda en profundidad recursiva | $O(S+E+K)$ | El límite de recursión de Python falla en cadenas largas de salas; una pila explícita no mejora la cola y complica el orden por rondas |
| Conjuntos disjuntos por región | casi lineal | Las salidas son dirigidas, así que fusionar regiones es incorrecto |
| Cola de prioridad por costo | $O((S+E)\log S)$ | No hay costos que ordenar y exigiría un montículo sin necesidad |

**Estructuras propias y por qué.** Todo es `list` direccionada por entero, sin `dict`, `set`, `sorted` ni `list.sort` (principio I). `ColaLista` es una `list` con índice de cabeza: `list.pop(0)` costaría $O(n)$ y `deque` está prohibido. `IndiceLlaves` es un arreglo ordenado de ids distintos con búsqueda binaria propia: el rango de una llave es su posición, de modo que «menor id» se reduce a comparar enteros (D3 y D4). Las salidas se guardan en listas planas por sala (inicio y fin), ordenadas una sola vez en $O(E)$ porque cada sala tiene pocas salidas.

**Complejidad.** La exploración cuesta $O(S+E+K)$: cada sala se encola una vez, cada salida se examina una vez y cada llave se obtiene una vez. El índice de llaves añade un factor $\log K$ al construirse y al resolver ids a rangos, $O((E_c+L)\log K)$ con $E_c$ salidas cerradas y $L$ ubicaciones. El ordenamiento por ronda aporta $O(S\log S)$ en el peor caso, una ronda muy ancha. Por eso afirmamos casi lineal y no lineal puro; SC-004 se comprueba midiendo (M2), no por la cota.

**Ciclos del grafo de testigos.** Si no hay victoria, una segunda fase continúa sobre la misma exploración, sin reiniciarla ni explorar por llave: atraviesa las puertas bloqueadas, etiqueta cada sala nueva con la llave que la libera y guarda la puerta testigo (D6). Para cada llave inobtenible se toma su ubicación alcanzada primero y se agrega una arista hacia la llave que libera esa sala. Una arista por llave forma una función parcial, así que los ciclos son disjuntos y se enumeran en $O(K)$ con una pasada de colores, cada uno desde su llave de menor id. Tres lemas sostienen que no hay ciclos falsos. Sean $R$ la región alcanzada, $O$ las llaves obtenidas y $U$ el resto:

1. **U es un bloqueo real.** Si alguna llave de $U$ se pudiera obtener, la primera en obtenerse estaría en una sala fuera de $R$ detrás de una puerta cuya llave está en $U$ y aún no se tiene: contradicción con que $R$ es un punto fijo.
2. **Cada arista es real.** Se registra solo si existe una ruta desde $R$ hasta la sala de la llave cuya última puerta cerrada exige la llave siguiente, y esa puerta se incluye en el reporte para verificarla a mano.
3. **Las alternativas no ocultan una salida.** Si una llave tiene rutas por las puertas de $J_1$ y $J_2$, ambas llaves están en $U$ (si una estuviera en $O$, la sala sería alcanzable). Elegir una no oculta una vía libre.

Decisión tomada: se reportan los ciclos del grafo de testigos y no las combinaciones de rutas alternativas, cuya enumeración es exponencial. Esto cumple la definición de ciclo de FR-012. Las alternativas descartadas son repetir una exploración por llave bloqueada ($O(K\,(S+E))$, prohibido por FR-025), componentes fuertemente conexas (reportan componentes y no ciclos concretos) y enumerar todos los ciclos elementales (exponencial).

**Consulta de llaves, presupuesto y persistencia (D7).** La ubicación de las llaves llega por un método propio de la fuente de datos (`GET /criptas/{id}/llaves`). En red cuenta como solicitud, respeta el presupuesto y los reintentos (principio V). Se guarda en `criptas/<id>/llaves.json` dentro de la carpeta que se reinicia cuando cambia la versión: con la misma versión, la segunda verificación lee disco y no usa red (FR-020); con otra versión se vuelve a consultar (FR-021). Si la ubicación no está disponible o el presupuesto no alcanza, el resultado es «resolubilidad no verificada», que no es un veredicto (FR-022).

**Replay y cargas sin verificar (D8).** `--replay` y continuar una partida guardada no verifican: no gastan solicitudes ni bloquean una partida que ya existe. Una partida iniciada con `--forzar` queda registrada y se puede reproducir. `--verificar` y `--bench` no importan `arcade` ni abren la vista (principio III).

### Comparación medida

**Reproducción:** `uv run python -m cripta --bench --semilla 42`, sección «Resolubilidad», implementada en [src/cripta/bench.py](../src/cripta/bench.py). Entorno y semilla como en §11; cada tiempo es el mejor de 3 a 5 corridas, salvo la ingenua, que se ejecuta una vez. Las cifras completas están en [mediciones.txt](../specs/001-resolubilidad/mediciones.txt); con la misma semilla los conteos coinciden entre ejecuciones y los tiempos varían. Las criptas se generan por semilla: región base conectada, cadena de $K=S/10$ llaves donde la puerta $j$ exige la llave $j-1$, ramas decorativas, ubicaciones repetidas e ids de sala permutados.

**M1: verificación frente a repetir la exploración por llave.**

| Salas $S$ | Salidas $E$ | Llaves $K$ | Verificación | Operaciones | Ingenua | Operaciones | Ingenua / verificación |
|----------:|------------:|-----------:|-------------:|------------:|--------:|------------:|-----------------------:|
| 200       | 409         | 20         | 0,972 ms     | 429         | 1,358 ms | 8 181      | 1,4 veces              |
| 2 000     | 4 121       | 200        | 10,940 ms    | 4 321       | 141,621 ms | 824 201  | 12,9 veces             |
| 20 000    | 41 237      | 2 000      | 147,926 ms   | 43 237      | omitida | omitida     | no medida              |

La ingenua pierde en los dos tamaños medidos y la brecha crece con $K$: de 1,4 a 12,9 veces. Por conteo, las operaciones de la verificación crecen 10 veces por cada 10 veces de tamaño, y las de la ingenua 100 veces. A 200 salas la ventaja en tiempo es pequeña; el contraste solo es claro desde 2 000 salas.

**M2: escalado al multiplicar por 10.** De 200 a 2 000 salas el tiempo crece 11,25 veces y las operaciones 10,07; de 2 000 a 20 000, 13,52 veces y 10,01. Ambos cocientes son menores que 15, como pide SC-004, pero el segundo está cerca del límite: el factor $\log K$ y el ordenamiento por ronda explican que el tiempo crezca más que las operaciones.

**M3: cripta de referencia del paquete.** El paquete `datos_offline` no trae `cripta_<id>_llaves.json`, así que la medición imprime «sin llaves en el paquete». Cuando el paquete traiga llaves, la misma medición verifica la cripta real sin red y marca si tarda menos de 200 ms. No hay cifra real de la cripta de referencia en esta ejecución.

**M7: límite de 200 ms sin red.** El esqueleto más grande del paquete tiene 50 salas, así que se genera una cripta sintética de 500 salas ($E=1\,027$, $K=50$). Resultó resoluble y se verificó en 2,571 ms, muy por debajo de 200 ms (SC-003). La prueba automatizada `test_limite_200ms_cripta_sintetica_grande` comprueba el mismo límite con el mejor de 3 corridas. Los tamaños de 2 000 y 20 000 salas se miden solo en M1, sin exigir un límite en una prueba.

**M4: arreglo ordenado frente a tabla hash propia**, a 20 000 salas ($K=2\,000$, 4 092 consultas):

| Medida | Arreglo ordenado | Tabla hash |
|--------|-----------------:|-----------:|
| Solo consultas | 5,911 ms | 6,185 ms |
| Construcción y consultas | 16,293 ms | 19,956 ms |

El arreglo es 1,22 veces más rápido que el hash en la medición completa, así que la regla de decisión (cambiar solo si el hash gana por más de 2 veces) conserva el arreglo. El hash no ahorra el orden: el rango por id exige ordenar los ids de todos modos, y la tabla se suma a ese costo.

**M5: costo del reporte en la variante con ciclo.**

| $S$ | $E$ | Sin reporte (resoluble) | Con reporte (un ciclo) | Salidas examinadas |
|----:|----:|------------------------:|-----------------------:|-------------------:|
| 2 000  | 4 121  | 10,997 ms  | 11,140 ms  | 4 121 de 4 121   |
| 20 000 | 41 237 | 148,282 ms | 152,076 ms | 41 237 de 41 237 |

El reporte cuesta cerca de 1 % a 3 % sobre la verificación y examina cada salida una sola vez: no repite exploraciones. El tiempo con reporte crece 13,65 veces al multiplicar por 10 el tamaño. La comparación usa una cripta resoluble del mismo tamaño y semilla, no la misma cripta sin reporte, porque el modelo no ofrece una verificación sin reporte; es una aproximación.

**M6: orden por ronda con `ordenar`**, a 20 000 salas (17 rondas muy anchas): ordenar las rondas cuesta 45,175 ms frente a 0,046 ms de solo copiarlas, un sobrecosto de 30,1 % de los 149,698 ms de la verificación completa. Es el costo de cumplir el empate por menor id (FR-008). Es aceptable porque el escalado de M2 sigue menor que 15; si dejara de serlo, la salida correcta sería enmendar la spec antes del código (principio VII) y no relajar el orden en silencio.

**Límites de esta medición.** Una ejecución, una semilla, en un solo equipo. Las criptas sintéticas tienen una cadena lineal de llaves, que es el peor caso para la ingenua, y no representan todas las criptas posibles. M3 no tiene dato real mientras el paquete no traiga llaves.

## 13. Niebla de guerra e ir a (Parte II, §3.3, §3.4 y §5.3)

**Necesidad y elección.** El jugador debe ver solo lo que conoce y poder viajar a una sala explorada por la ruta de menor costo, con pasos ordinarios. El modelo (`modelo/Conocimiento.py`, `modelo/Rutas.py`) no conoce HTTP, archivos ni vista. Las razones completas de cada decisión (D1 a D15) están en [research.md](../specs/002-niebla-ir-a/research.md); aquí se resumen con las mediciones de [mediciones.txt](../specs/002-niebla-ir-a/mediciones.txt) (`--bench --semilla 42`, K1 a K9).

**Estado de sala y memoria de puertas (D1, D2).** Dos listas planas de enteros pequeños: `estado_sala[id]` (0 desconocida, 1 avistada, 2 explorada) y `puerta[clave]` (0 sin observar, 1 abierta, 2 cerrada), con `clave = origen * 4 + dirección` (N 0, S 1, E 2, O 3). Un solo entero por sala evita estados imposibles y hace trivial serializar (`5n + 2` valores). Descartadas: dos listas booleanas, un atributo en `SalaJuego`, una lista de ids explorados con búsqueda lineal y `dict` o `set` (prohibidos por el principio I).

**Entrantes (D3).** Una lista por id de sala con las salidas que llegan a ella, construida una vez en $O(E)$ al ensamblar. La usan la observación de puertas y el Dijkstra inverso. Recorrer todas las salas para hallarlas costaría $O(S)$ por consulta.

**Observación al final de la acción (D4).** Las puertas se observan una vez por acción, al final de `consumir_tiempo` y antes de `finalizar`, dentro del intervalo del historial. Como la memoria solo guarda el último estado, produce el mismo estado final que un gancho por cada cambio de puerta, sin acoplar `Puertas` al conocimiento. El gancho queda como plan B. No se observa tras el pergamino: correría fuera de un intervalo y no sería invertible.

**`lista_asignada` frente a copia completa (D5).** `Historial_Retroceso.asignar(lista, posicion, valor)` registra `[lista, posicion, valor_anterior]` y no registra si el valor no cambia. Cada cambio cuesta $O(1)$ al registrar y al invertir; la antorcha produce a lo sumo unos 16 por entrada. K3 con 20 000 salas y 1 000 cambios: registrar e invertir 6,5 ms frente a 197,3 ms copiando el conocimiento en cada cambio (100 002 000 valores copiados). Con 200 salas son 1,8 ms frente a 3,8 ms: la copia crece con el mapa y `lista_asignada` solo con los cambios.

**Costo (D6).** `SalidaSimple` y `SalidaVecina` ganan `costo`. Una salida sin costo, o con costo menor que 1, vale 100 (el segundo caso deja un aviso en la bitácora de arranque). Con costo cero el criterio «costo más distancia» podría girar entre salas de igual distancia; además el viaje se corta a tantos pasos como salas exploradas (motivo `sin_ruta`).

**Dijkstra inverso con parada anticipada (D7).** Una búsqueda desde el destino sobre las salidas entrantes sirve a cualquier origen y se detiene al fijar la sala actual. Con costos positivos todo candidato de costo mínimo ya está fijado cuando se fija la sala actual, así que la parada no pierde empates. El desempate es menor id de la sala destino y luego N, S, E, O. Dos listas (`distancia` y `marca` por generación) se reutilizan entre búsquedas y evitan reinicializar $S$ posiciones por paso. Complejidad $O((V + E)\log V)$ sobre lo explorado.

| Alternativa | Resultado medido | Motivo |
|-------------|------------------|--------|
| BFS con `ColaLista` (K8) | En los 50 pares de 2 000 salas devolvió una ruta de mayor costo; ninguna igual ni menor | Correcto solo con costos iguales; FR-023 pide menor costo total, no menos salas |
| Dijkstra desde el origen (K6) | 1 086 ms frente a 869 ms | El desempate del primer paso es más delicado y no gana |
| Dijkstra inverso completo, sin parada (K6) | 4 042 ms frente a 869 ms | Recorre todo lo alcanzable en cada paso |
| Reutilizar distancias entre pasos (K6) | 151 ms frente a 869 ms (5,75 veces menos) | No cumple FR-026 si el conocimiento cambia durante el viaje; ver abajo |
| Floyd-Warshall o precálculo | $O(X^3)$ o memoria $O(X^2)$ | Se invalida con cada puerta observada |
| A\* | No aplica | No hay coordenadas para una heurística admisible |

**K6 y la regla de más de 2 veces.** La regla de D7 («se conserva el inverso con parada salvo que otra alternativa gane por más de 2 veces») compara solo alternativas que cumplen FR-026, que exige recalcular antes de cada paso con el conocimiento vigente. Reutilizar las distancias gana por 5,75 veces, pero no cumple FR-026 cuando el conocimiento cambia durante el viaje: una puerta recordada abierta que resulta cerrada invalida las distancias de forma no local. En K6 las cuatro estrategias coinciden en el costo de ruta solo porque en esa medición el conocimiento no cambia entre pasos. Por eso la alternativa queda fuera de la comparación y se conserva el inverso con parada. **Mejora futura:** reutilizar las distancias mientras el conocimiento no cambie y recalcular en cuanto cambie (por ejemplo, comparando la longitud del registro del conocimiento entre pasos).

**Montículo propio (D8, K7).** `MonticuloMinimo` con tres listas paralelas (prioridad, desempate, elemento), comparación lexicográfica entera, sin `heapq` y con eliminación perezosa. No se reutiliza `HeapAgendaEventos`, atado a `Evento` y al historial. K7 (2 000 salas, búsqueda completa): perezoso 14,6 ms, con decremento de clave e índice 8,3 ms (el perezoso cuesta 1,75 veces, sin llegar a 2, así que se conserva) y selección lineal $O(V^2)$ 147,0 ms; las tres dan las mismas distancias.

**Qué se comparte con el cazador (D9, §5.3).** Se comparten `MonticuloMinimo`, la regla de desempate y `modelo/Rutas.py`; el predicado `usable(salida)` lo aporta cada llamador. «Ir a» pasa uno sobre el conocimiento del jugador (salas exploradas, salidas recordadas abiertas); el cazador de la spec 003 conoce el mapa completo y pasará uno sobre el estado real. Costo de compartir: una llamada de predicado por arista relajada.

**Viaje por pasos y registro como comentario (D10, D11).** `ViajeControlador` hace exactamente un paso por llamada con `Aplicacion.mover`, por el flujo común de acción: consume tiempo, corren los eventos, queda en `partida.log` y el pergamino revierte solo el último paso, sin continuar el viaje. La orden aceptada se escribe como `# ir_a <sala>` antes del primer paso; el lector del registro omite los comentarios y reproduce los `mover`. Descartadas: bucle bloqueante, encolar todos los pasos (viola FR-026) y registrar el viaje como una acción compuesta (el pergamino lo revertiría entero).

**Fugas de información corregidas (D15).** `actualizar_vecindad` dejó de copiar `tiene_enemigos` y `tiene_objetos` de las vecinas, y `es_salida_final` se muestra solo para vecinas exploradas (FR-011, FR-014).

**Complejidad medida.**

| Operación | Costo | Medición |
|-----------|-------|----------|
| Estado de sala y puerta recordada | $O(1)$ | K1: 101, 112 y 112 ns (estado) con 200, 2 000 y 20 000 salas, razones ×1,11 y ×1,00; la búsqueda lineal crece ×9,6 y ×9,2 |
| Explorar por sala revelada | $O(4)$, $O(16)$ con antorcha | K2: 2,0 cambios por sala en los tres tamaños (razón ×1,00) |
| Registrar e invertir cambios | $O(1)$ por cambio | K3, arriba |
| Un paso de «ir a», referencia | $O((V + E)\log V)$ | K4: la cripta de referencia del paquete tiene 50 salas; media 0,144 ms y máximo 0,239 ms, menor que 5 ms |
| Un paso de «ir a», 2 000 y 20 000 salas | $O((V + E)\log V)$ | K5 (informativa): media 7,6 ms y 77,3 ms (×10,11; la cota $(V + E)\log V$ predice ×13,24) |
| Determinismo | | K9: K4 y K6 dos veces con la misma semilla dan resultados idénticos, sin ventana |

**K2 y el recolector de basura.** El criterio de K2 se evalúa por conteo de cambios al registro por sala revelada (no depende de la máquina), que da razón ×1,00. El tiempo por sala de 2 000 a 20 000 salas sube ×2,97 sin antorcha y ×1,98 con ella con el recolector de basura activo, porque este recorre las decenas de miles de entradas del registro. La segunda medición, con el recolector desactivado durante la exploración, da ×1,27 y ×1,13 (de 2,350 a 2,994 µs y de 5,661 a 6,408 µs por sala): el trabajo del algoritmo por sala no crece con el mapa y la diferencia es una pausa del entorno de ejecución. El tiempo con el recolector activo supera la razón de 1,5 y se informa así, sin cambiar el criterio.

**Dependencias y limitaciones.**

- **FR-025 depende de la spec 003.** Cada paso de «ir a» usa `mover`, así que consume el tiempo del movimiento ordinario; el costo de la salida como tiempo es de la spec 003. Mientras tanto consume el costo actual de mover.
- **FR-015 depende de la spec 004.** Esta spec entrega `instantanea()` y `restaurar()`, pero incluir el conocimiento en el formato binario de guardado corresponde a la 004. Mientras un guardado no lo traiga, al cargar se arma el conocimiento desde la sala actual (la sala actual explorada con sus puertas observadas y los destinos de sus salidas avistados) con el registro vacío.
- **Interfaz gráfica.** El mapa conocido es la tecla **C** y «ir a» es un clic sobre una sala explorada del mapa; no hay comandos de texto.
- **Reversión de `lista_agregada` (C8, FR-037).** Pasó a `pop()` del final, $O(1)$; la búsqueda anterior queda solo como respaldo si el último elemento no coincide.
- **Correcciones de pruebas.** T042 compara cada paso del viaje con un movimiento ordinario equivalente (FR-025 enmendado) en lugar de suponer el costo de la salida como tiempo; T054a comprueba que `mapa_conocido()` no escribe en la bitácora (FR-018 no se lo pide).
- **Carga de contenido de red.** Un paso del viaje puede cargar contenido de red de forma síncrona si la caché lo descartó.
- **Detección de daño.** Se compara la vida antes y después del paso: un daño y una curación iguales en el mismo paso no se detectan, y un daño calculado 0 por defensa no cuenta (C4).
- **Pergamino fallido.** Un pergamino fallido no cancela el viaje.

**Interpretación de FR-013.** El mapa conocido y el viaje leen nombre y salidas del esqueleto de la cripta, pero solo de las salas que ConocimientoJugador marca como exploradas (salidas_conocidas). El conocimiento no duplica nombres ni costos por diseño; lo que FR-013 prohíbe es usar el esqueleto completo, es decir, información de salas que el jugador no conoce.