# Investigación: Verificación de resolubilidad de la cripta

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Notación: S = salas, E = salidas (dirigidas), K = llaves distintas, L = ubicaciones de llaves,
Ec = salidas cerradas, U = llaves no obtenibles. Todas las decisiones respetan la constitución
(sin `dict`/`set` como índice, sin `heapq`, `bisect`, `collections`, `networkx`, `sorted()` ni
`list.sort()`).

No quedan marcadores NEEDS CLARIFICATION. Las decisiones que dependían de la spec están
resueltas en [plan.md](plan.md), sección "Decisiones tomadas".

---

## D1. Algoritmo de exploración

**Decisión**: exploración en anchura desde `sala_inicial`, con cola propia (`list` más índice de
cabeza) y una lista de espera por llave. Cada salida cerrada cuya llave aún no se tiene se anota
en la espera de esa llave; al obtener la llave se liberan sus salidas en espera. La exploración
NO se detiene al ganar: continúa hasta agotar la región, porque FR-007 exige todas las llaves
obtenibles.

Pasos:

1. Se marca la sala inicial como alcanzada (ronda 0) y se encola.
2. Se procesa cada sala de la ronda: primero se obtienen sus llaves no obtenidas, en orden de
   id; al obtener una llave se agrega al orden y se liberan sus esperas (los destinos pasan a la
   ronda siguiente si no estaban alcanzados).
3. Luego se recorren las salidas de la sala en orden fijo. Salida abierta, o cerrada con llave ya
   obtenida: se alcanza el destino. Cerrada con llave no obtenida: se anota en la espera de la
   llave.
4. Al vaciar la cola, la región alcanzable es definitiva (punto fijo).

Cada sala se encola una vez, cada salida se examina una vez y cada salida en espera se libera una
vez, y cada llave se obtiene una vez: O(S + E + K) sin contar la construcción del índice (D3).

**Salidas dirigidas**: cada salida es un arco propio con la llave que declara su lado. En
`cripta-01`, la salida E de la sala 2 hacia la 5 exige `itm_llave_bronce` y la O de la 5 hacia la
2 está abierta: el arco 2 a 5 espera y el arco 5 a 2 se recorre libre. No se infiere ningún
arco simétrico.

**Orden de llaves**: es el orden de obtención (ronda, id de sala, id de llave). Cada llave queda
después de todas las que se necesitaron para alcanzar su sala, porque la sala se alcanza solo
cuando la llave de su puerta ya se obtuvo (en una ronda anterior).

**Alternativas**:

| Alternativa | Costo | Motivo |
|-------------|-------|--------|
| Repetir la exploración completa cada vez que se obtiene una llave | O(K · (S + E)) | Es la que FR-024 prohíbe. Se conserva solo en `--bench` como contraste (M1) |
| Iterar hasta punto fijo sobre todas las puertas (relajar hasta que nada cambie) | O(K · E) peor caso | Misma familia que la anterior; sin mejora de cota |
| Búsqueda en profundidad recursiva con pila de llamadas | O(S + E + K) | La recursión de Python (límite 1 000 por defecto) falla en cadenas largas de salas; una pila explícita no aporta sobre la cola y complica el orden por rondas |
| Estructura de conjuntos disjuntos por región | casi lineal | Las salidas son dirigidas, así que fusionar regiones es incorrecto |
| Cola de prioridad por costo | O((S + E) log S) | No hay costos; el montículo sería `heapq` o un montículo propio sin necesidad |

---

## D2. Orden determinista y regla de empate

**Decisión**: la exploración avanza por rondas. Una ronda es el conjunto de salas encoladas
mientras se procesaba la anterior. Antes de procesar una ronda, sus salas se ordenan por id con
el `ordenar` propio sobre la porción de la cola. Las salidas de cada sala se recorren por
(id de la sala destino, dirección) y las llaves de una sala por id de llave (orden fijado una
vez al construir las estructuras).

Esto da un orden total de procesamiento (ronda, id de sala), que es exactamente la regla de la
aclaración 3: una llave publicada en varias ubicaciones se obtiene en la alcanzable primero y,
con empate de ronda, en la de menor id de sala. Toda ubicación posterior de la misma llave se
ignora para el orden y para el reporte principal, pero el reporte de bloqueo lista todas las
ubicaciones cuando ninguna es alcanzable (FR-011).

Se anota que el resultado no depende del orden dentro de una ronda: el conjunto de salas de la
ronda siguiente es el mismo; el ordenamiento por id solo fija el orden de las llaves y el desempate
entre ubicaciones.

**Costo**: la suma de los tamaños de las rondas es S, así que el ordenamiento aporta O(S log S) en el
peor caso (una ronda muy ancha) y casi O(S) en cadenas, donde `ordenar` elige inserción
(listas de 16 o menos, o casi ordenadas). Se mide en M6.

**Alternativa**: no ordenar y usar el orden de cola, que es determinista pero no cumple el
empate "menor id de sala". Se descarta mientras la spec conserve esa regla; si M6 mostrara que el
sobrecosto rompe SC-004, la salida correcta es enmendar la spec antes del código (principio VII),
no relajar el diseño en silencio.

---

## D3. Índice de ids de llave

**Contexto**: las llaves son cadenas (`itm_llave_bronce`). Se necesita un índice entero por
llave para guardar los datos por llave en listas. El universo de llaves se arma una vez con los
ids de las salidas cerradas y de las ubicaciones.

**Decisión**: arreglo ordenado de ids distintos, ordenado con `ordenar`, con búsqueda binaria
propia. El índice entero de una llave es su posición, de modo que el orden de índices es el orden
por id: "menor id" se reduce a comparar enteros.

| Criterio | Arreglo ordenado + búsqueda binaria | Tabla hash propia (hash polinomial determinista, direccionamiento abierto) |
|----------|--------------------------------------|----------------------------------------------------------------------------|
| Consulta | O(log K) | O(1) esperado |
| Construcción | O((Ec + L) log K) con búsqueda previa para no duplicar; o un `ordenar` de las Ec + L cadenas y una pasada de deduplicación | O(Ec + L) esperado más O(K log K) para asignar el rango por id |
| Rango por id | Gratis (posición) | Requiere ordenar los K ids de todas formas |
| Determinismo | Total | Exige función propia (no `hash()` de Python, que varía por proceso) y política de colisión fija |
| Código | Una búsqueda binaria de 10 líneas | Función de hash, sondeo, redimensionado y pruebas de colisión |
| Riesgo | Constante mayor por consulta | Más superficie de errores y de defensa en la evaluación |

Con K de decenas a miles y consultas solo por salida cerrada, la diferencia esperada es pequeña, y
el rango por id exige ordenar de todos modos. Se elige el arreglo ordenado y M4 mide la tabla
hash propia como alternativa, con la regla: se cambia solo si gana por más de 2 veces en la
verificación completa al mayor tamaño sintético.

**Precisión de complejidad** (decisión tomada): la exploración es O(S + E + K); el índice añade
O((Ec + L) log K), el factor log K aceptado. El plan y la presentación DEBEN decir esto, no
"lineal puro". El factor logarítmico solo afecta
al término del índice; con K proporcional a S, multiplicar el tamaño por 10 multiplica ese término
por 10 · log(10K) / log K, que es 13,3 con K = 1 000 y menor que 15 desde K de unos 600, y el
resto del costo es lineal. Para K menores el índice pesa muy poco frente a la exploración.
SC-004 se comprueba midiendo (M2), no por esta cota.

Las ubicaciones se resuelven una vez a índice de llave y las salidas cerradas también, durante
la construcción; la exploración solo usa enteros.

---

## D4. Estructuras de datos del modelo

**Decisión**: todo en `list`, direccionado por entero.

- Por sala (índice = id de sala; `IndiceSalas` para id a sala del esqueleto, y listas paralelas
  de tamaño `max_id + 1` para el estado): ronda de alcance (-1 = no alcanzada), etiqueta de la
  fase especulativa y puerta testigo.
- Salidas en formato compacto por sala (inicio y fin dentro de listas planas): destino, índice de
  llave (-1 si abierta) y dirección. Se ordenan por (destino, dirección) una vez; cada sala
  tiene a lo sumo 4 o 5 salidas, así que el costo total es O(E).
- Por llave (índice = rango por id): `obtenida`, `espera` (lista de índices de salida),
  `ubicaciones` (lista de pares sala y enemigo, por sala), `puesto` en el orden.
- Cola: `Cola_Lista` con `list` y un índice de cabeza. NO se usa `list.pop(0)` (O(n)) ni `deque`.

**Alternativas**: `dict` por llave (prohibido), `set` de alcanzadas (prohibido), una lista
enlazada propia como cola (sin ventaja sobre `list` e índice de cabeza, más asignaciones).

---

## D5. Condición de resolubilidad

**Decisión**: la cripta es resoluble si, al terminar la fase 1, `llave_salida` fue obtenida y se
recorrió una salida cerrada con `llave_salida` cuyo destino es `sala_salida`, partiendo de una
sala alcanzada. La bandera se activa en el momento en que esa salida se libera o se recorre con la
llave ya obtenida.

Cubre los bordes de la spec:

- Llave inalcanzable: `llave_salida` en U, no resoluble.
- Llave obtenible pero ninguna puerta que la requiere conduce a `sala_salida`: la bandera no se
  activa, no resoluble.
- Varias puertas con la misma llave: la lista de espera las libera todas.
- Trampas y cierres automáticos: se ignoran (`cierre_automatico` no cambia la salida).
- `llave_salida` en la sala inicial: se obtiene en la ronda 0 y se incluye en el orden junto con
  las demás.

Motivos de no resolubilidad que el resultado distingue: la llave de salida no es obtenible, o es
obtenible pero ninguna puerta con esa llave llega a `sala_salida`.

---

## D6. Reporte de bloqueo y ciclos desde la misma exploración

**Decisión**: si la fase 1 termina sin resolubilidad, se continúa en la misma estructura (misma
cola, sin reiniciar y sin explorar por llave) con una fase 2 especulativa que atraviesa las
puertas bloqueadas y etiqueta cada sala nueva con la llave que la liberó.

Fase 2:

1. La frontera bloqueada son las esperas pendientes: puertas cerradas desde una sala alcanzada
   cuya llave está en U. Se listan por (rango de llave, orden de inserción).
2. Se recorre cada puerta de la frontera: el destino, si no estaba alcanzado, se alcanza con
   etiqueta = llave de esa puerta y se registra la puerta testigo (origen, dirección, destino).
3. Desde cada sala nueva se exploran sus salidas con las mismas rondas y orden de D2. Una salida
   abierta, o cerrada con llave obtenida, hereda la etiqueta de la sala. Una salida cerrada con llave
   en U reetiqueta al destino con esa llave y registra esa puerta como testigo.
4. Cada sala y cada salida se procesa una sola vez: O(S + E).

Grafo de dependencias: para cada llave K de U se toma su ubicación alcanzada primero en fase 2
(D2) y se agrega una arista K a etiqueta(sala). Una sola arista por llave: es una función
parcial. Sumideros posibles: llave sin ubicación publicada (dato faltante), ubicación en una
sala que ni siquiera la fase 2 alcanza (sala desconectada) o ubicación en una sala inexistente
del esqueleto (dato inconsistente). Todo recorrido termina en un sumidero o en un ciclo, y los ciclos de
una función parcial son disjuntos, de modo que la enumeración es lineal y no hay explosión
combinatoria.

Enumeración de ciclos: se marca con una pasada de colores (sin visitar, en recorrido, cerrado)
qué llaves están en un ciclo; luego se recorren los rangos de menor a mayor y, al encontrar una
llave de ciclo aún no emitida, se emite ese ciclo empezando en ella. Como los rangos siguen el
orden por id y el primer miembro encontrado es el menor, cada ciclo empieza en su llave de menor
id, con el mismo sentido (cada llave seguida de la que su puerta exige), y la lista queda
ordenada por ese id sin ordenamiento adicional: O(K). Una llave que depende de sí misma
(`llave_salida` detrás de la única puerta que ella abre) es un ciclo de longitud 1.

### Por qué el método no reporta ciclos falsos con caminos alternativos

Sean R la región alcanzada al terminar la fase 1, O las llaves obtenidas y U el resto.

**Lema 1 (U es un bloqueo real).** Ninguna llave de U se puede obtener en ninguna secuencia de
juego. Si existiera una, sea X la primera de U en obtenerse. Antes de X solo se tendrían llaves
de O, y la fase 1 ya calculó el punto fijo con ellas (R no crece), así que la sala de X no está
en R, y para llegar a ella habría que cruzar una puerta cuya llave está en U y no se tiene
todavía. Contradicción. Por tanto, toda llave de un ciclo reportado es realmente inobtenible; en
particular, un ciclo nunca se reporta en una cripta resoluble porque la fase 2 solo corre cuando
no lo es.

**Lema 2 (cada arista es real).** La arista K a J se registra solo si existe una ruta desde R
hasta una sala de K cuya última puerta cerrada requiere J, con J en U. La puerta testigo
concreta (sala origen, dirección, sala destino) se guarda y se incluye en el reporte, así que
cada arista de un ciclo es verificable a mano.

**Lema 3 (las alternativas no ocultan una salida).** Supóngase que K tiene rutas alternativas por
puertas de las llaves J1 y J2, y que el método registra K a J1 por orden. Si J2 estuviera en O, esa
puerta se habría abierto en la fase 1 y la sala de K estaría en R, así que K estaría en O: no es
el caso. Por tanto, J2 también está en U. Elegir J1 en vez de J2 no puede ocultar una vía libre: toda
alternativa exige una llave de U, y por el Lema 1 ninguna de U se obtiene. Tampoco se puede
"romper" un ciclo tomando la alternativa, porque la cadena de dependencia de J2 también termina en
un sumidero o en otro ciclo de la misma función parcial, ambos incluidos en el reporte (llaves sin
ubicación, desconectadas o ciclos).

**Ejemplo**: A está detrás de una puerta que exige B y de otra que exige C; B está detrás de A;
C está detrás de A. Por orden se registra A a B, B a A: se reporta el ciclo A, B. Es real: ninguna
de las dos puertas de A se puede abrir, porque B y C solo se obtienen después de A. Si en cambio C
estuviera en una sala libre, C estaría en O, la puerta de C estaría abierta, A estaría en O y no
habría ciclo, que es lo que se espera.

**Alineación con FR-012**: FR-012 define ciclo como una cadena de llaves encontrada por la
exploración en la que cada llave está detrás de una puerta que requiere la siguiente, y exige
incluir todos los ciclos distintos que la exploración encuentre sin omitir ninguno. No exige
enumerar las combinaciones de rutas alternativas. El método cumple esa definición: reporta todos
los ciclos del grafo de testigos y no los ciclos adicionales que existirían eligiendo otra
alternativa (en el ejemplo, A, C no se lista aparte), cuya enumeración sería exponencial en el
peor caso. Decisión tomada: se aceptan los ciclos del grafo de testigos.

**Alternativas**:

| Alternativa | Problema |
|-------------|----------|
| Repetir una exploración por cada llave bloqueada para ver qué libera | O(K · (S + E)); prohibido por FR-025 |
| Grafo con todas las alternativas (O) y componentes fuertemente conexas de Tarjan | Lineal, pero reporta componentes, no ciclos concretos, y una componente puede contener ciclos que dependen de alternativas |
| Enumerar todos los ciclos elementales (Johnson) | Exponencial; se necesitaría lógica propia nueva |
| Detectar el ciclo solo desde `llave_salida` | Omite ciclos de otras llaves (FR-012 pide todos) |

---

## D7. Consulta de llaves, persistencia y presupuesto

**Decisión**: método nuevo y abstracto `key_locations(crypta_id) -> dict` en `CryptDataSource`
(`GET /criptas/{id}/llaves`), implementado por las tres clases existentes. El detalle está en
[contracts/adaptador-llaves.md](contracts/adaptador-llaves.md).

- `NetworkAdapter`: usa `_request`, por lo que cuenta en `_requests_made`, respeta el presupuesto
  y los reintentos 429 (principio V).
- `AdaptadorOffline`: primero `AlmacenDisco.leer_llaves`, luego `cripta_<id>_llaves.json` del
  paquete; si no hay ninguno lanza `FileNotFoundError` (resultado: no verificable).
- `Guardar_Llamadas_API`: graba `cripta_<id>_llaves.json` con la firma ya usada (parámetro `datos`).
- `AlmacenDisco`: `criptas/<id>/llaves.json`, dentro de la carpeta que `validar_cripta` borra al
  cambiar la versión. Con la misma versión, la segunda verificación lee disco y NO solicita red
  (FR-020, SC-005). Con versión distinta, la carpeta se reinicia y se vuelve a consultar (FR-021).
- `CriptaService.obtener_ubicaciones_llaves`: disco primero (si `_cripta_en_disco`), si no, fuente.
  `PresupuestoAgotado`, `RuntimeError`, `OSError`, `ValueError`, `FileNotFoundError` y
  `NotImplementedError` se traducen a "ubicación no disponible", que no es un veredicto
  (FR-022). La consulta suma al presupuesto; si este no alcanza, el resultado es "no verificada"
  (decisión tomada).
- **Fuentes falsas de pruebas**: las de `test_partida.py`, `test_inventario.py`,
  `test_combate_efectos.py` y `test_guardados.py` DEBEN recibir la consulta devolviendo "sin
  datos"; la selección de pruebas del README DEBE seguir pasando y la suite completa de pruebas/
  NO DEBE tener fallas nuevas respecto de una línea base registrada antes de implementar.

**Nota de persistencia en `--verificar`**: la validación por versión necesita `validar_cripta`,
hoy dentro de `preparar_persistencia`, que además consulta la versión del catálogo (una solicitud
innecesaria). Se propone separar `validar_cripta_en_disco(detalles)` para que `--verificar` no
gaste esa solicitud.

**Alternativas**: leer las llaves del contenido de cada sala (`/contenido`) en vez de un endpoint
propio: costaría ceil(S/10) solicitudes y mezcla botín con enemigos no publicados como
`enemigo`; descartado por el hecho del proyecto de que el servicio publica `/llaves`. Cachear en
un archivo único junto a `criptas.json`: se pierde la invalidación por versión.

---

## D8. Integración con partida, consola y bench

**Inicio de partida**. `InicioPartidaControlador.iniciar` verifica justo después de cargar el
esqueleto y antes de cargar el contenido de salas (así no se gastan solicitudes de contenido si la
partida se bloquea). Tres desenlaces:

| Situación | Efecto en la partida | Aviso |
|-----------|----------------------|-------|
| Resoluble | Inicia | Resultado y orden de llaves en la bitácora y en el aviso |
| No resoluble sin `--forzar` | NO inicia (`ok=False`, `estado.activa=False`) | Reporte completo como `motivo` |
| No resoluble con `--forzar` | Inicia | Reporte disponible en la bitácora |
| Ubicación no disponible | Inicia, con o sin `--forzar` | "resolubilidad no verificada", sin veredicto |

`--forzar` entra por `bootstrap` a `Aplicacion` (no a la vista), de modo que la vista solo muestra
`motivo` con el mecanismo actual de `terminado` en `ventana.iniciar_partida`.

**Replay y cargas**: `--replay` y continuar una partida guardada NO verifican, como dice la
sección de supuestos de la spec. Se pasa `iniciar_partida(..., verificar=False)` para no gastar
solicitudes ni bloquear una partida que ya existe. Una partida iniciada con `--forzar` queda
registrada y se puede reproducir.

**`--verificar CRIPTA`**: grupo mutuamente excluyente con `--replay`, `--bench` y `--grafica`.
Construye fuente, `AlmacenDisco`, `CriptaService`, `VerificacionControlador`; nunca importa
`arcade` ni la vista. Códigos 0, 1 y 2 según FR-018a (ver
[contracts/verificar-cli.md](contracts/verificar-cli.md)). Con `--offline` usa `AdaptadorOffline`
y NO realiza solicitudes de red (SC-006).

**`--bench --semilla N`**: `bootstrap` pasa la semilla a `bench.main`. Semilla vacía equivale a 42.
Generador sintético (determinista por `random.Random(semilla)`):

- Región base de B salas conectada por un árbol aleatorio y salidas abiertas, para que cada
  repetición de la exploración ingenua cueste S + E.
- Cadena de K llaves: la puerta j exige la llave j-1 y la llave j está en la sala que esa puerta
  abre, de modo que cada llave libera la siguiente región.
- Ramas decorativas y un pequeño porcentaje de ubicaciones repetidas, todo por la semilla.
- Los ids de sala se permutan por la semilla para que el orden por id no coincida con el orden de
  la cadena.
- Variante no resoluble: la última llave de la cadena exige una llave anterior de modo que cierra
  un ciclo, para medir M5.

La ingenua se implementa solo en `bench.py`, marcada como alternativa descartada, igual que
`_ListaOrdenada` en la medición de la agenda.

**Alternativa**: ejecutar la verificación al abrir el menú para todas las criptas. Se descarta:
multiplica solicitudes por cripta y rompe el presupuesto (principio V).
