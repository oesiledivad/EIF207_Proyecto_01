# Investigación y decisiones: Línea de tiempo y puntos de control

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Cada decisión indica qué requisitos atiende, las alternativas consideradas y por qué se eligió. Las
mediciones previstas (L1 a L5) se ejecutan con `--bench` y sus resultados finales van a
`DECISIONES.md`, secciones 17 (§5.5) y 18 (§5.6, retroceso).

## D1. Qué guarda la línea: el estado observable (FR-005, FR-006, FR-014)

**Decisión.** La línea guarda el estado observable que exige el resumen: sala, vida, vida máxima,
ataque, defensa y velocidad del jugador; resultado de la partida; inventario; efectos; sala y vida
de cada enemigo, y el conocimiento del jugador (estado de cada sala y memoria de cada salida). No
guarda la agenda, el azar, las trampas ni el rastro.

**Alternativas.** (a) Estado completo del juego por evento: permitiría re-simular, pero exige
serializar la agenda y el azar en cada punto de control y re-ejecutar eventos para consultar; (b)
re-simular desde el inicio con el registro de acciones: viola FR-015 (más de K acciones).

**Por qué.** El enunciado pide reconstruir el estado que se **muestra**; guardar más agrega memoria
sin cambiar ninguna consulta. Con el estado observable no hace falta re-simular, de modo que el
estado del azar no es necesario (FR-019 aplica solo si se re-simula; queda documentado).

## D2. Representación: ranuras y bitácora de cambios (FR-014)

**Decisión.** El estado observable es una lista de ranuras con índices fijos: 0 a 6 jugador y
resultado, 7 inventario (tupla de textos), 8 efectos (tupla), 9 a 9+5n-1 conocimiento (n salas y 4n
salidas), y luego dos ranuras por enemigo (sala y vida) en el orden en que la línea lo ve cambiar por
primera vez. La bitácora son cuatro listas paralelas: tiempo, ranura, valor anterior y valor nuevo.
Solo se anexa un cambio si el valor nuevo es distinto del vigente.

**Alternativas.** Un registro por objeto con referencias (como el historial de retroceso): no es
serializable y las referencias cambian al cargar. Un diccionario de claves: prohibido.

**Por qué.** Índices enteros dan acceso O(1) sin tablas hash; guardar el valor anterior permite
reconstruir en las dos direcciones (D7) y recortar con el pergamino restaurando el vector vivo.

## D3. Granularidad: un registro por evento (FR-001)

**Decisión.** La simulación expone `al_terminar_evento` (opcional, `None` por defecto) y lo llama
al terminar cada evento con el reloj actual. El controlador captura ahí. También captura después de
ejecutar la acción del jugador y al cerrar la acción (observación de puertas de la spec 002).

**Por qué.** `historia <t>` puede caer entre dos acciones del jugador; con registro solo por acción
no se podría distinguir lo ocurrido antes y después de t.

## D4. Cómo se detecta qué cambió (FR-006)

**Decisión.** (a) Jugador, resultado, inventario y efectos: se leen y comparan en cada captura (el
inventario está acotado por su capacidad). (b) Enemigos: el historial de retroceso avisa a un
observador opcional en cada `registrar`; si es un cambio de `sala` o `vida` de un `Enemigo`, el
enemigo se marca sucio y su valor anterior queda como base si es la primera vez que cambia. En la
captura solo se leen los sucios. (c) Conocimiento: se leen las entradas nuevas del registro
cronológico de la spec 002 desde un cursor.

**Alternativas.** Comparar todos los enemigos de la cripta en cada evento: O(enemigos) por evento,
multiplicado por decenas de cazadores.

**Por qué.** El historial ya ve todo cambio de estado durante una acción (P1 §4.6), y extenderlo es
lo que propone el análisis del grupo. Un enemigo que nunca cambió está en su sala inicial con su
vida inicial desde el instante 0, así que no necesita ranura.

## D5. Marcas por acción y búsqueda binaria propia (FR-003, FR-008, FR-016)

**Decisión.** Antes de ejecutar cada acción del jugador se anexa una marca `[instante, posición]`.
Los instantes de las marcas crecen estrictamente (toda acción consume al menos 1). `historia <t>`
busca con búsqueda binaria propia la última marca con instante ≤ t; si es igual a t, el estado es el
de la marca (antes de decidir); si no, avanza en la bitácora mientras el tiempo sea ≤ t, dentro de
una sola acción. `historia #k` usa la marca k-1 directamente.

**Alternativa.** Recorrido lineal de marcas: O(N) por consulta.

## D6. Puntos de control (FR-013, FR-015, FR-016, FR-018)

**Decisión.** Punto de control 0 al crear la línea (posición 0). Luego, al anexar la marca m con
m múltiplo de K y m > 0, se copia el vector vivo. El punto de control de la acción a es el índice
`a // K` (O(1)), su siguiente `a // K + 1`.

**K por defecto.** Provisional 50; se fija con L1 como el menor K cuyo tiempo de consulta peor
queda cómodamente bajo 50 ms con la menor memoria.

## D7. Dirección de reconstrucción (FR-015, FR-019, FR-031)

**Decisión.** Hacia adelante desde el punto de control anterior (aplicando `después`) o hacia atrás
desde el siguiente o desde el vector vivo si no hay siguiente (aplicando `antes`), el que tenga menos
cambios. Ninguna dirección recorre más de K acciones.

**Alternativas.** Re-simular desde el punto de control (necesita agenda y azar y ejecutar eventos);
solo hacia adelante; solo hacia atrás. L2 compara adelante, atrás y el más cercano.

## D8. Recorte por pergamino (FR-010, FR-011, FR-012)

**Decisión.** Cuando el pergamino revierte la acción k, la bitácora se trunca a la posición de la
marca k invirtiendo en el vector vivo los cambios quitados, se quitan las marcas desde k y los puntos
de control tomados en esas marcas, y se vuelve el cursor del conocimiento al valor guardado en la
marca. Luego se captura en el instante actual, y ahí entra el descuento del pergamino (FR-011). Una
acción que falla o lanza error usa el mismo recorte.

## D9. Guardado (FR-024 a FR-027, FR-034)

**Decisión.** `VERSION_CUERPO` pasa de 2 a 3 y se agrega un cuerpo `ID_LINEA` con la instantánea
del conocimiento, K, la tabla de enemigos con ranura y la línea completa (valores etiquetados: nulo,
entero, booleano, texto y tupla de textos). Un cuerpo versión 2 se rechaza con «guardado de la Parte
I: formato incompatible». Al cargar se restaura el conocimiento con `restaurar()` (cierra FR-015 de
la spec 002), se re-enlazan los enemigos por identificador y el historial de retroceso queda vacío.

## D10. `--replay --hasta` (FR-021 a FR-023)

**Decisión.** Se reproduce el registro completo sin vista y se consulta la línea en t con la misma
función que `historia`. Si t supera el reloj final se imprime el estado final y el instante de fin.

## D11. Interfaz (FR-028)

**Decisión.** La tecla H abre un panel de entrada: dígitos, `#`, retroceso y Enter. El resultado se
muestra en un panel de texto. La tecla figura en la ayuda; no se agrega al menú de Esc porque su panel muestra solo nueve opciones y la nueva ocultaba «Terminar la partida».

## D12. `--bench`

L1 memoria (celdas y bytes con `tracemalloc`) y tiempo de consulta (media y peor) para K = 1, 10,
50, 200 y sin puntos de control, sobre una partida de 5 000 acciones jugada en la cripta más grande
del paquete con semilla fija. Las líneas con otros K se reconstruyen alimentando la misma bitácora,
así todas describen la misma partida. L2 adelante, atrás y más cercano con K por defecto. L3 costo
de la captura por acción (con y sin línea). L4 recorte por pergamino en partidas de 1 000 y 10 000
acciones. L5 (§5.6, retroceso) registrar e invertir 10 000 intervalos con y sin observador, y
cambios por intervalo en la partida de L1.

## Mediciones previstas

| Id | Qué | Requisito |
|----|-----|-----------|
| L1 | memoria y consulta por K y sin puntos de control | FR-029, FR-030, SC-003, SC-005 |
| L2 | adelante, atrás y más cercano | FR-031 |
| L3 | costo de captura por acción | 20 ms de la spec 003 |
| L4 | recorte proporcional a lo revertido | FR-012 |
| L5 | historial de retroceso con la carga nueva | FR-032 |
