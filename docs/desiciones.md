# Documento de Decisiones de Diseño — P2: Combate y Efectos

## 1. Agenda de eventos (§4.1)

### Problema
El bucle principal necesita obtener repetidamente el evento con menor `tiempo_siguiente`
(desempatado por número de secuencia), soportar cancelación de eventos cuando un actor
muere o un efecto se cancela, y soportar reprogramación cuando cambia la velocidad de
un actor con una acción ya programada. Esta operación se ejecuta decenas de miles de
veces por partida según el enunciado, y en nuestras pruebas con la cripta de referencia
observamos entre X y Y eventos simultáneos en la agenda durante combates con varios
enemigos activos. [completar con el conteo real de --bench]

### Alternativas consideradas
- **Lista ordenada por tiempo_siguiente, reinsertada en cada cambio**: descartada porque
  insertar en orden es O(n) y, con cientos de reprogramaciones por partida (cada acción
  de cada actor reprograma su siguiente evento), degrada el rendimiento linealmente con
  el tamaño de la agenda.
- **Heap binario con eliminación activa de eventos cancelados**: descartada porque un
  heap no soporta localizar un elemento arbitrario en O(log n) sin mantener un índice
  posición-por-evento aparte (equivalente al "decrease-key" de Dijkstra), lo cual añade
  complejidad de implementación y de mantenimiento del invariante sin necesidad real
  dado que el patrón de la segunda alternativa la resuelve más simple.
- **Heap binario con invalidación perezosa (elegida)**: cada evento tiene un flag
  `valido`; cancelar es O(1) (solo se marca), y la basura se descarta sola cuando sale
  del heap por ser el mínimo.

### Decisión
Heap binario propio (arreglo + sift-up/sift-down) con invalidación perezosa. Cancelar
un evento es `evento.valido = False` (O(1)). Reprogramar invalida el evento viejo del
actor e inserta uno nuevo, actualizando la referencia `actor._proximo_evento`. Cada
actor mantiene como máximo una referencia activa a su propio evento, lo cual acota la
cantidad de basura que puede acumularse en el heap en un momento dado.

### Análisis de complejidad
- `insertar`: O(log n)
- `extraer_siguiente`: O(log n) amortizado (puede descartar varios inválidos en el
  camino, pero cada uno se descarta exactamente una vez en su vida)
- `cancelar`: O(1)
- `peek`: O(1) amortizado

### Evidencia empírica
[Pendiente — correr `--bench` con cargas sintéticas de 100, 500 y 2000 eventos
simultáneos, y comparar `insertar`/`extraer_siguiente` contra una lista ordenada por
inserción como alternativa descartada, tal como exige §8.5 del enunciado.]

### Límites conocidos
Si la tasa de cancelación/reprogramación es mucho mayor que la de ejecución real de
eventos (por ejemplo, cientos de actores cambiando de velocidad constantemente sin que
nadie actúe), el heap podría llenarse de basura más rápido de lo que se vacía, aunque
en el peor caso sigue siendo O(log n) por operación individual.


## 2. Combate e IA de enemigos (§2.6, §2.8)

### Problema
Calcular daño determinista (usando `random.Random(semilla)` propio, nunca el generador
global), aplicar vida/muerte, y decidir la acción de cada enemigo según su
comportamiento (guardián, errante, rastreador) en cada uno de sus turnos.

### Alternativas consideradas
- **Un solo método gigante en `Enemigo` con `if/elif` por tipo de comportamiento**:
  descartada por violar el principio de responsabilidad única y dificultar agregar
  comportamientos nuevos sin tocar código ya probado.
- **Tabla de despacho (dict comportamiento → función)**: descartada porque el curso
  prohíbe usar `dict` como estructura de resolución (§7).
- **Herencia con template method (elegida)**: `Enemigo.decidir_accion` resuelve la parte
  común (atacar si comparte sala con el jugador) y delega en `_decidir_movimiento`,
  que cada subclase (`Guardian`, `Errante`, `Rastreador`) implementa por separado.

### Decisión
Patrón template method vía herencia; cada subclase de `Enemigo` implementa
`_decidir_movimiento`. El despacho de clase según el string de comportamiento del
catálogo (`"guardián"`/`"errante"`/`"rastreador"`) usa `match/case`, no `dict`.

### Análisis de complejidad
`decidir_accion` es O(1) para Guardián y Errante (recorren a lo sumo 4 salidas).
Rastreador es O(k) donde k es el número de salidas de su sala actual (máximo 4),
consistente con el requisito de §4.7 de que el costo sea proporcional a las salidas de
la sala, no al tamaño de la cripta.

### Evidencia empírica
[Pendiente — medir con `--bench` el tiempo de `decidir_accion` para cada
comportamiento, y confirmar que no crece con el tamaño de la cripta.]

### Límites conocidos
El daño mínimo de 1 (`max(1, ataque + azar - defensa)`) puede hacer que combates entre
actores con defensa muy alta respecto al ataque se vuelvan extremadamente largos; no es
un error, es el comportamiento especificado, pero afecta el rendimiento percibido en
criptas con enemigos de alta defensa.


## 3. Efectos temporales (§2.10)

### Problema
Veneno, cambio de velocidad temporal, regeneración y antorcha son efectos que se
reprograman a sí mismos periódicamente o expiran después de un tiempo fijo, y deben
poder cancelarse (ej. un antídoto cancela el veneno) sin afectar otros eventos del
mismo actor.

### Alternativas consideradas
- **Un único evento "efectos" por actor que revisa todos los efectos activos en cada
  tick**: descartada porque requeriría un tick de reloj fijo (el juego no tiene rondas,
  es dirigido por eventos) y desperdiciaría ciclos revisando efectos inactivos.
- **Un evento independiente por tipo de efecto, reutilizando la misma agenda y el mismo
  mecanismo de invalidación perezosa que las acciones de actor (elegida)**: cada efecto
  es simplemente otro `tipo` de evento despachado desde `Simulacion.ejecutar_evento`.

### Decisión
Cada actor guarda una referencia a su evento de veneno/regeneración/fin-de-velocidad
por separado de su `_proximo_evento` de acción normal, porque son líneas de tiempo
independientes que pueden coexistir. `procesar_muerte` cancela las cuatro referencias
a la vez para que ningún efecto le sobreviva a un actor muerto.

### Análisis de complejidad
Cada pulso de efecto es O(log n) (una extracción + una inserción en la agenda), igual
que cualquier otro evento — no se introduce ninguna estructura nueva.

### Evidencia empírica
[Pendiente — medir cuántos eventos de efectos coexisten en una partida típica con
varios enemigos envenenados/regenerando a la vez, y confirmar que el overhead sobre la
agenda es marginal frente a los eventos de acción.]

### Límites conocidos
El veneno tiene duración fija de 400 unidades (5 pulsos de 80); si se vuelve a aplicar
veneno sobre un actor ya envenenado, la implementación actual **reinicia** el contador
de duración en vez de acumular o tomar el máximo — es una decisión de diseño razonable
pero vale la pena dejarla explícita por si la defensa pregunta por el caso borde.


## 4. Caché de catálogo e integración de precarga (§4.3, §4.4, extra de P2)

### Problema
Resolver referencias de catálogo (ids de tipo → ficha) sin pedir cada una por separado,
sin repetir una solicitud de red si la ficha ya está en memoria o en disco, y sin
superar el tope de fichas en memoria.

### Alternativas consideradas
- **`dict` como caché**: prohibido explícitamente por el enunciado (§7).
- **Cache_Fichas con tabla hash propia + LRU (ya implementada por el equipo, integrada
  acá)**: se usa tal cual, sin reimplementarla — `asegurar_fichas` solo decide qué ids
  faltan y arma los lotes de hasta 10 (§3.4), delegando el almacenamiento en la caché
  existente.

### Decisión
`CriptaService.asegurar_fichas` deduplica los ids pedidos (lista + comparación lineal,
no `set`, por la misma razón de §7) y solo solicita al catálogo los que no están ya en
`Cache_Fichas`.

### Análisis de complejidad
Deduplicar k ids es O(k²) en el peor caso (comparación lineal por cada id), aceptable
porque k es el número de tipos distintos en un lote de contenido, típicamente ≤ 10.

### Evidencia empírica
[Pendiente — medir aciertos/fallos de caché reales en una partida completa, y comparar
solicitudes de red usadas contra `presupuesto_solicitudes` de la cripta.]

### Límites conocidos
La deduplicación O(k²) dejaría de ser trivial si una sola sala pudiera declarar
decenas de tipos distintos de enemigos/trampas, lo cual no ocurre en el formato de
cripta descrito en el enunciado.
