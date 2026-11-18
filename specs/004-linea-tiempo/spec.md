# Feature Specification: Línea de tiempo y puntos de control

**Feature Branch**: `eliseo`

**Created**: 2026-11-17

**Status**: Draft

**Input**: User description: "Línea de tiempo. El pergamino de retroceso sigue limitado a 5 acciones; la línea de tiempo es independiente y permite consultar, sin modificar la partida, el estado en cualquier instante desde el inicio. Estado en el instante t: el estado después de ejecutar todos los eventos con tiempo menor o igual que t; si a t le corresponde una decisión del jugador, es el estado justo antes de tomarla. Comando historia <t> e historia #k (estado justo antes de la acción número k del jugador), que muestra como mínimo reloj, sala del jugador, vida y estadísticas, inventario, efectos activos, enemigos de esa sala con su vida y el mapa conocido en ese momento (spec 002, FR-017). La consulta no consume tiempo virtual, no se registra como acción y no altera ningún estado del juego ni del historial de retroceso. --replay partida.log --hasta <t> reproduce la partida hasta t e imprime el mismo resumen sin instanciar la vista. Las acciones revertidas con un pergamino dejan de existir en la línea de tiempo; consultar un instante posterior al reloj actual se rechaza. Memoria: se permiten copias completas del estado (puntos de control) pero no más de una cada K acciones del jugador, con K configurable con --checkpoint-cada K y valor por defecto justificado con mediciones; una consulta no puede aplicar o deshacer cambios de más de K acciones; fuera de los puntos de control solo se guarda lo necesario para reconstruir los cambios; se puede reconstruir hacia adelante (re-simulando, con el estado del generador de azar en el punto de control) o hacia atrás (invirtiendo cambios), y la elección se documenta con evidencia. Ubicar el punto de control más cercano es una búsqueda frecuente; al usar un pergamino la línea se recorta sin recorrer toda la historia. Persistencia: guardar y cargar conserva la línea completa y el conocimiento del jugador (spec 002, FR-015); el formato binario cambia y un archivo de la Parte I se detecta como incompatible o se migra de forma explícita, nunca se carga en silencio. Rendimiento: la consulta historia tarda como máximo 50 ms en una partida de al menos 5000 acciones con K por defecto; --bench mide memoria y tiempo de consulta para al menos tres valores de K y la alternativa sin puntos de control. Además se repiten las mediciones del historial de retroceso de la Parte I con la carga nueva (§5.6). Escenarios de aceptación obligatorios (Apéndice B, línea de tiempo): (1) historia con t mayor que el reloj se rechaza; (2) historia después de un pergamino no muestra las acciones revertidas; (3) varios eventos en el mismo instante t: historia <t> muestra el estado después de todos; (4) historia no consume tiempo, no se registra en partida.log y no modifica el historial de retroceso; (5) --replay --hasta t con t posterior al final muestra el estado final e indica que la partida terminó antes; (6) se carga un archivo de la Parte I: se reporta la incompatibilidad o se migra explícitamente, nunca se carga en silencio."

## Clarifications

### Session 2026-11-17

- Q: Cuando alguien intenta cargar un archivo de guardado de la Parte I, ¿qué hace el programa? → A: Lo rechaza: reporta que el formato es incompatible y no lo carga. No se ofrece migración.
- Q: Si una partida guardada con un K se carga con `--checkpoint-cada` y otro valor, ¿qué K usa? → A: El K guardado con la partida; si la bandera trae otro valor, se avisa y se ignora.
- Q: Al cargar una partida, ¿el pergamino puede revertir acciones tomadas antes de guardar? → A: No. Como en la Parte I, el historial de retroceso empieza vacío al cargar; solo se revierten acciones tomadas después de la carga.
- Q: Si el jugador usa un pergamino y el reloj vuelve a t, ¿`historia <t>` muestra el pergamino ya descontado? → A: Sí. El descuento ocurre en t, antes de la siguiente decisión, así que `historia <t>` coincide con el estado que el jugador ve en pantalla.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar el estado de un instante pasado (Priority: P1)

Durante la partida, el jugador escribe `historia <t>` y ve cómo estaba la partida en el instante virtual t: el reloj, la sala donde estaba, su vida y estadísticas, el inventario, los efectos activos, los enemigos de esa sala con su vida y el mapa que conocía en ese momento. El estado en t es el que queda después de ejecutar todos los eventos con tiempo menor o igual que t; si en t le tocaba decidir al jugador, se muestra el estado justo antes de esa decisión. Consultar no cambia nada de la partida.

**Why this priority**: Es el núcleo de la capacidad y la única forma de observar la línea de tiempo durante el juego.

**Independent Test**: Se juega una partida corta con una semilla fija, se anota el resumen visible antes de cada acción del jugador y se comprueba que `historia <t>` reproduce exactamente cada resumen anotado, para instantes de decisión y para instantes intermedios.

**Acceptance Scenarios**:

1. **Given** una partida con reloj actual 1200, **When** el jugador consulta `historia 1500`, **Then** la consulta se rechaza con un mensaje que indica que el instante es posterior al reloj actual, y nada de la partida cambia (Apéndice B, caso 1).
2. **Given** una partida en la que varios eventos (por ejemplo, el turno de un enemigo, un tic de veneno y el cierre automático de una puerta) ocurren en el mismo instante 700, **When** el jugador consulta `historia 700`, **Then** el resumen muestra el estado después de todos esos eventos (Apéndice B, caso 3).
3. **Given** un instante t entre dos decisiones del jugador en el que ocurrieron eventos del reloj, **When** el jugador consulta `historia <t>`, **Then** el resumen incluye los eventos con tiempo menor o igual que t y ninguno posterior.
4. **Given** un instante t en el que al jugador le correspondía decidir, **When** el jugador consulta `historia <t>`, **Then** el resumen es el estado justo antes de esa decisión.
5. **Given** una partida en curso, **When** el jugador consulta `historia <t>` para cualquier t válido, **Then** el reloj virtual no avanza, no se agrega ninguna línea a partida.log, la cantidad de acciones que el pergamino puede revertir no cambia y los enemigos no actúan (Apéndice B, caso 4).
6. **Given** el instante 0, **When** el jugador consulta `historia 0`, **Then** se muestra el estado inicial de la partida, con la sala inicial como única sala explorada y sus vecinas avistadas.

---

### User Story 2 - Consultar por número de acción (Priority: P1)

El jugador escribe `historia #k` y ve el estado justo antes de su acción número k, contando solo las acciones que siguen existiendo en la partida.

**Why this priority**: Es la segunda forma de consulta exigida y la más natural para revisar decisiones propias.

**Independent Test**: Se juega una partida de N acciones, se anota el resumen antes de cada una y se comprueba que `historia #k` coincide con el anotado para cada k de 1 a N.

**Acceptance Scenarios**:

1. **Given** una partida con 10 acciones del jugador, **When** consulta `historia #1`, **Then** ve el estado inicial, antes de su primera acción.
2. **Given** una partida con 10 acciones del jugador, **When** consulta `historia #7`, **Then** ve el estado justo antes de la séptima acción, igual al que vio en pantalla en ese momento.
3. **Given** una partida con 10 acciones del jugador, **When** consulta `historia #11`, **Then** ve el estado actual, antes de la acción que aún no tomó.
4. **Given** una partida con 10 acciones del jugador, **When** consulta `historia #12` o `historia #0`, **Then** la consulta se rechaza con un mensaje y nada cambia.

---

### User Story 3 - La línea de tiempo respeta el pergamino de retroceso (Priority: P1)

Cuando el jugador usa un pergamino, las acciones revertidas dejan de existir en la línea de tiempo: la línea describe la historia de la partida tal como quedó.

**Why this priority**: Sin esta regla la línea mostraría una historia que ya no ocurrió, y es un caso obligatorio del Apéndice B.

**Independent Test**: Se juegan 6 acciones, se usan dos pergaminos y se juega una acción distinta; se comprueba que la línea solo contiene las 4 primeras acciones y la nueva, y que ningún instante muestra el resultado de las acciones revertidas.

**Acceptance Scenarios**:

1. **Given** una partida en la que el jugador se movió al norte en el instante 500 y luego usó un pergamino, **When** consulta cualquier instante desde 500 hasta el reloj actual, **Then** el resumen no muestra el movimiento al norte ni nada de lo que ocurrió después de él (Apéndice B, caso 2).
2. **Given** 8 acciones del jugador y luego un pergamino, **When** consulta `historia #8`, **Then** ve el estado actual (la octava acción ya no existe y la próxima acción será la nueva octava).
3. **Given** un pergamino usado y luego una acción distinta, **When** consulta un instante posterior a esa acción, **Then** ve el resultado de la acción nueva, no el de la revertida.
4. **Given** una partida larga, **When** el jugador usa un pergamino, **Then** el recorte de la línea cuesta en proporción a lo revertido, no a la longitud total de la partida.

---

### User Story 4 - Consultar sin interfaz con --replay --hasta (Priority: P2)

Quien revisa una partida ejecuta `--replay partida.log --hasta <t>` y obtiene en consola el mismo resumen que mostraría `historia <t>`, sin que se abra ninguna ventana.

**Why this priority**: Permite verificar la línea de tiempo de forma automática y es el mecanismo de reproducción de los escenarios, pero depende de que la consulta ya exista.

**Independent Test**: Se juega una partida, se consulta `historia <t>` en el juego para varios t y se compara cada resumen con la salida de `--replay` del mismo partida.log con `--hasta <t>`.

**Acceptance Scenarios**:

1. **Given** un partida.log y un t menor o igual que el reloj final de la partida, **When** se ejecuta `--replay partida.log --hasta <t>`, **Then** se imprime el resumen del instante t, idéntico al de `historia <t>`, y no se abre ninguna ventana.
2. **Given** un partida.log cuya partida terminó en el instante 3000, **When** se ejecuta `--replay partida.log --hasta 9000`, **Then** se imprime el estado final y un aviso de que la partida terminó antes del instante pedido, en 3000 (Apéndice B, caso 5).
3. **Given** un valor de `--hasta` que no es un entero mayor o igual que 0, **When** se ejecuta el comando, **Then** termina con un mensaje de error y sin reproducir.
4. **Given** `--hasta` sin `--replay`, **When** se ejecuta el programa, **Then** termina con un mensaje de error que indica que `--hasta` solo se usa con `--replay`.

---

### User Story 5 - Guardar y cargar conserva la línea de tiempo y el mapa conocido (Priority: P2)

Al guardar la partida se guarda también la línea de tiempo completa y el conocimiento del jugador. Al cargarla, el jugador puede consultar los mismos instantes y obtiene los mismos resúmenes que antes de guardar, y ve el mismo mapa conocido. Un archivo guardado con el formato de la Parte I nunca se carga en silencio.

**Why this priority**: Es exigido por el enunciado y cierra el pendiente de la spec 002 (FR-015), pero depende de la línea de tiempo y del conocimiento ya existentes.

**Independent Test**: Se juega una partida, se anotan varios resúmenes de `historia`, se guarda, se cierra, se carga y se comprueba que los resúmenes y el mapa conocido son idénticos.

**Acceptance Scenarios**:

1. **Given** una partida con línea de tiempo, **When** se guarda y se carga, **Then** `historia <t>` y `historia #k` dan exactamente los mismos resúmenes que antes de guardar, para todo t y k válidos.
2. **Given** una partida con salas exploradas, avistadas y puertas recordadas, **When** se guarda y se carga, **Then** el mapa conocido es idéntico al del momento de guardar, incluidas las puertas recordadas con un estado distinto del real.
3. **Given** un archivo de guardado de la Parte I, **When** el jugador intenta cargarlo, **Then** se informa que el formato es incompatible y la partida no se carga (Apéndice B, caso 6).
4. **Given** una partida cargada, **When** el jugador sigue jugando, **Then** la línea de tiempo continúa desde donde quedó y las consultas de instantes anteriores a la carga siguen funcionando.
5. **Given** una partida cargada, **When** el jugador usa un pergamino, **Then** solo puede revertir acciones tomadas después de la carga, como ya ocurre en la Parte I, y la línea de tiempo se recorta igual que en la historia 3.

---

### User Story 6 - Memoria acotada y consulta rápida en partidas largas (Priority: P2)

La línea de tiempo no guarda una copia completa del estado en cada acción. Solo se permiten copias completas, llamadas puntos de control, como máximo una cada K acciones del jugador, y entre ellas solo se guarda lo necesario para reconstruir los cambios. K se configura con `--checkpoint-cada K` y tiene un valor por defecto justificado con mediciones. Ninguna consulta aplica o deshace cambios de más de K acciones del jugador.

**Why this priority**: Es la restricción de estructuras de datos que se evalúa (§5.5), pero solo tiene sentido una vez que la consulta existe.

**Independent Test**: Se ejecuta una partida sintética de 5000 acciones con distintos K y se comprueba que el número de puntos de control no supera acciones / K + 1, que cada consulta procesa como máximo K acciones y que el resultado coincide con el de K = 1.

**Acceptance Scenarios**:

1. **Given** `--checkpoint-cada 50` y una partida de 5000 acciones, **When** termina la partida, **Then** hay como máximo 101 puntos de control.
2. **Given** cualquier K y cualquier instante consultado, **When** se reconstruye el estado, **Then** se aplican o deshacen cambios de como máximo K acciones del jugador.
3. **Given** dos valores distintos de K y la misma partida, **When** se consulta el mismo instante, **Then** los dos resúmenes son idénticos.
4. **Given** `--checkpoint-cada 0`, un valor negativo o un valor no entero, **When** se inicia el programa, **Then** termina con un mensaje de error antes de iniciar la partida.
5. **Given** que no se indica `--checkpoint-cada`, **When** se inicia una partida, **Then** se usa el valor por defecto documentado.

---

### User Story 7 - Medir la línea de tiempo y revisar el retroceso de la Parte I (Priority: P3)

El modo `--bench` mide la memoria y el tiempo de consulta de la línea de tiempo para al menos tres valores de K y para la alternativa sin puntos de control, compara la reconstrucción hacia adelante con la reconstrucción hacia atrás, y repite las mediciones del historial de retroceso de la Parte I con la carga nueva.

**Why this priority**: Es la evidencia exigida por la constitución (principio VI) y el Documento de Decisiones, pero depende de que la capacidad funcione.

**Independent Test**: Se ejecuta `--bench` con una semilla y se comprueba que imprime, para cada valor de K, la memoria usada y el tiempo de consulta, y las mediciones del retroceso, sin abrir ventanas.

**Acceptance Scenarios**:

1. **Given** `--bench` con una semilla, **When** se ejecuta, **Then** se imprimen memoria y tiempo de consulta para al menos tres valores de K y para la alternativa sin puntos de control, sobre partidas sintéticas deterministas de al menos 5000 acciones.
2. **Given** `--bench`, **When** se ejecuta, **Then** se imprime el tiempo de consulta reconstruyendo hacia adelante y hacia atrás sobre las mismas partidas.
3. **Given** `--bench`, **When** se ejecuta, **Then** se repiten las mediciones del historial de retroceso de la Parte I con cazadores, costos variables y línea de tiempo activa.
4. **Given** `--bench` dos veces con la misma semilla, **When** se comparan las partidas generadas, **Then** son idénticas.

---

### Edge Cases

- `historia` sin argumento, con texto no numérico, con t negativo o con `#` sin número: se rechaza con un mensaje y nada cambia.
- `historia <t>` con t igual al reloj actual: muestra el estado actual.
- `historia` después de que la partida terminó (victoria o derrota), mientras la sesión sigue abierta: se permite y muestra instantes hasta el reloj final.
- Un instante en el que el jugador murió: muestra vida 0 y el estado después de todos los eventos de ese instante.
- Un instante en medio de un viaje «ir a»: cada paso es una acción y la consulta lo trata como cualquier otra acción.
- Un instante en el que la antorcha exploró vecinas: el mapa conocido del resumen las incluye; si esa entrada fue revertida con un pergamino, no las incluye.
- Un pergamino justo después de un punto de control: el punto de control posterior a lo revertido deja de existir.
- Usar un pergamino no es una acción del jugador ni consume tiempo (Parte I §2.11), pero descuenta un pergamino del inventario; ese descuento aparece en la línea en el instante en que ocurrió.
- Las acciones que no consumen tiempo (navegar el inventario, seleccionar un objeto) no cuentan como acciones para `historia #k` ni para K.
- Un partida.log que termina sin acción final: `--replay --hasta` con t posterior al último instante también indica que la partida terminó antes.
- Un archivo de guardado de la Parte II dañado o truncado: se rechaza con un mensaje, igual que en la Parte I.
- Una partida cargada se guarda de nuevo: la línea conserva toda la historia, incluida la anterior a la primera carga.
- Una partida guardada con un K se carga con `--checkpoint-cada` y otro valor: se usa el K guardado y se avisa que la bandera se ignora (FR-027).

## Requirements *(mandatory)*

### Functional Requirements

**Consulta en partida**

- **FR-001**: El estado en el instante t DEBE ser el estado después de ejecutar todos los eventos con tiempo menor o igual que t; si a t le corresponde una decisión del jugador, DEBE ser el estado justo antes de tomarla.
- **FR-002**: El sistema DEBE ofrecer el comando `historia <t>`, con t entero mayor o igual que 0, que muestra el estado en el instante t.
- **FR-003**: El sistema DEBE ofrecer el comando `historia #k`, con k entero mayor o igual que 1, que muestra el estado justo antes de la acción número k del jugador; `#1` es el estado inicial y `#(N+1)`, con N acciones existentes, es el estado actual.
- **FR-004**: Una consulta con t mayor que el reloj actual, con k fuera de 1 a N+1, o con un argumento mal formado DEBE rechazarse con un mensaje que indique el motivo.
- **FR-005**: El resumen de una consulta DEBE mostrar como mínimo: reloj, sala del jugador, vida y estadísticas del jugador, inventario, efectos activos, enemigos de la sala del jugador con su vida y el mapa conocido por el jugador en ese instante.
- **FR-006**: El estado mostrado por una consulta DEBE ser idéntico al estado que la partida tuvo en ese instante.
- **FR-007**: Una consulta NO DEBE consumir tiempo virtual, registrarse en partida.log, contar como acción, alterar el estado del juego, alterar el generador de azar ni alterar el historial del pergamino de retroceso.
- **FR-008**: Son acciones del jugador, para `historia #k` y para K, las acciones que consumen tiempo virtual, incluido cada paso de «ir a». Usar un pergamino y navegar o seleccionar en el inventario no lo son.
- **FR-009**: Las consultas DEBEN poder hacerse también después de que la partida terminó, mientras la sesión siga abierta.

**Interacción con el pergamino de retroceso**

- **FR-010**: Las acciones revertidas con un pergamino, y todo lo ocurrido después de ellas, DEBEN dejar de existir en la línea de tiempo; la numeración de acciones continúa desde la última acción que sigue existiendo.
- **FR-011**: El descuento del pergamino usado DEBE aparecer en la línea de tiempo en el instante al que volvió el reloj, antes de la siguiente decisión del jugador; `historia` de ese instante DEBE mostrar el pergamino ya descontado.
- **FR-012**: Recortar la línea al usar un pergamino DEBE costar en proporción a lo revertido, no a la longitud total de la línea.

**Memoria y puntos de control**

- **FR-013**: El sistema PUEDE guardar copias completas del estado (puntos de control), pero como máximo una cada K acciones del jugador.
- **FR-014**: Fuera de los puntos de control, el sistema DEBE guardar solo la información necesaria para reconstruir los cambios; la memoria total DEBE crecer con la cantidad de cambios ocurridos más un punto de control cada K acciones, nunca con «acciones por tamaño del estado».
- **FR-015**: Una consulta NO DEBE requerir aplicar o deshacer cambios de más de K acciones del jugador.
- **FR-016**: Ubicar el punto de control más cercano a un instante pedido NO DEBE costar en proporción a la cantidad de puntos de control.
- **FR-017**: K DEBE configurarse con `--checkpoint-cada K`, con K entero mayor o igual que 1; un valor inválido DEBE terminar el programa con un mensaje antes de iniciar la partida.
- **FR-018**: Sin `--checkpoint-cada`, K DEBE tomar un valor por defecto justificado con las mediciones de FR-030.
- **FR-019**: Si la reconstrucción re-simula desde un punto de control, el punto de control DEBE incluir el estado del generador de azar, de modo que la re-simulación produzca exactamente los mismos eventos.
- **FR-020**: El mapa conocido del resumen DEBE reconstruirse con la interfaz que provee la spec 002 (FR-017), sin depender del estado actual del mapa.

**Consulta sin interfaz**

- **FR-021**: `--replay partida.log --hasta <t>` DEBE reproducir la partida hasta el instante t e imprimir el mismo resumen que `historia <t>`, sin instanciar la vista.
- **FR-022**: Si t es posterior al último instante de la partida registrada, `--replay --hasta` DEBE imprimir el estado final e indicar que la partida terminó antes y en qué instante.
- **FR-023**: `--hasta` con un valor que no es entero mayor o igual que 0, o sin `--replay`, DEBE terminar con un mensaje de error.

**Persistencia**

- **FR-024**: Guardar y cargar la partida DEBE conservar la línea de tiempo completa; después de cargar, toda consulta DEBE dar el mismo resumen que antes de guardar.
- **FR-025**: El archivo de guardado DEBE incluir el conocimiento del jugador; después de cargar, el mapa conocido DEBE ser idéntico al del momento de guardar (cierra spec 002, FR-015).
- **FR-026**: El archivo de guardado DEBE declarar una versión de formato nueva. Un archivo de la Parte I DEBE detectarse y reportarse como incompatible, y no se carga; no se ofrece migración.
- **FR-027**: Después de cargar, la línea de tiempo DEBE continuar con las acciones nuevas y K DEBE ser el guardado con la partida; si `--checkpoint-cada` trae otro valor, DEBE avisarse que se ignora.
- **FR-034**: Al cargar, el historial del pergamino de retroceso DEBE empezar vacío, como en la Parte I: el pergamino solo revierte acciones tomadas después de la carga.

**Interfaz**

- **FR-028**: La interfaz DEBE permitir escribir `historia <t>` e `historia #k` y mostrar el resumen o el motivo del rechazo, sin cerrar ni pausar la partida de forma permanente.

**Rendimiento y evidencia**

- **FR-029**: Una consulta `historia` DEBE tardar como máximo 50 ms en una partida de al menos 5000 acciones del jugador, con K por defecto, medido en el equipo local sin red ni renderizado.
- **FR-030**: `--bench` DEBE medir memoria y tiempo de consulta de la línea de tiempo para al menos tres valores de K y para la alternativa sin puntos de control, sobre partidas sintéticas deterministas por semilla de al menos 5000 acciones.
- **FR-031**: `--bench` DEBE medir la reconstrucción hacia adelante y la reconstrucción hacia atrás sobre las mismas partidas.
- **FR-032**: `--bench` DEBE repetir las mediciones del historial de retroceso de la Parte I con la carga nueva (cazadores, costos variables y línea de tiempo activa).
- **FR-033**: `--bench` y `--replay --hasta` NO DEBEN instanciar la vista.

### Key Entities

- **Línea de tiempo**: la historia de la partida tal como quedó, desde el instante 0 hasta el reloj actual, que permite reconstruir el estado de cualquier instante.
- **Instante**: un valor del reloj virtual. Puede coincidir con una decisión del jugador o caer entre dos.
- **Acción del jugador**: una acción que consume tiempo virtual y que el pergamino puede revertir. Se numera desde 1.
- **Punto de control**: una copia completa del estado en un instante de decisión del jugador, como máximo una cada K acciones.
- **Cambio**: la información mínima para pasar de un estado al siguiente o al anterior, con el instante en que ocurrió.
- **Resumen**: lo que muestra una consulta: reloj, sala, vida, estadísticas, inventario, efectos, enemigos de la sala y mapa conocido.
- **Archivo de guardado**: contiene el estado de la partida, el conocimiento del jugador, la línea de tiempo y K, con una versión de formato que distingue la Parte I de la Parte II.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los seis escenarios del Apéndice B de la línea de tiempo (t mayor que el reloj, historia tras pergamino, varios eventos en el mismo instante, consulta sin efectos, replay más allá del final, archivo de la Parte I) se cumplen en pruebas automatizadas o en un partida.log que cita su FR.
- **SC-002**: En el 100% de los instantes probados de partidas con semilla fija, el resumen de `historia` coincide con el estado anotado en ese instante durante el juego.
- **SC-003**: Con al menos 5000 acciones del jugador y K por defecto, el 100% de las consultas medidas tarda como máximo 50 ms según `--bench`.
- **SC-004**: En el 100% de las consultas medidas, la cantidad de acciones aplicadas o deshechas es como máximo K.
- **SC-005**: Para al menos tres valores de K y la alternativa sin puntos de control, `--bench` reporta memoria y tiempo de consulta, y la memoria de la línea crece con los cambios más un punto de control cada K acciones.
- **SC-006**: Guardar y cargar conserva el 100% de los resúmenes consultados antes de guardar y el mapa conocido completo.
- **SC-007**: El 100% de los archivos de la Parte I probados se reportan como incompatibles y ninguno se carga.
- **SC-008**: Con `--bench` y con `--replay --hasta` se abren 0 ventanas de la interfaz.

## Assumptions

- El pergamino de retroceso, el registro de cambios por acción y el guardado binario de la Parte I ya existen; esta spec los extiende y repite sus mediciones (§5.6).
- El conocimiento del jugador ya ofrece instantánea, restauración, registro cronológico y reconstrucción (spec 002, FR-015 y FR-017, contrato de conocimiento serializable).
- El generador de criptas sintéticas deterministas de `--bench` ya existe (spec 003); esta spec lo extiende con partidas largas.
- El orden de los eventos de un mismo instante se resuelve como en la Parte I, por tiempo y número de secuencia.
- El rechazo de archivos de la Parte I usa la validación de versión que ya existe en el guardado; no se ofrece migración.
- La línea de tiempo se guarda en el mismo archivo de guardado que la partida, no en un archivo aparte.
- La consulta se muestra en la interfaz que ya existe; esta spec solo exige qué información se muestra, no su diseño visual.

## Out of Scope

- Cambiar el límite de 5 acciones del pergamino de retroceso o su forma de uso.
- Volver a jugar desde un instante pasado (bifurcar la partida); la línea solo se consulta.
- `historia #k` en `--replay`; la consulta sin interfaz solo usa `--hasta <t>`.
- Migrar archivos de guardado de la Parte I.
- El diseño visual del resumen en la interfaz gráfica.
