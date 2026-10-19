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
