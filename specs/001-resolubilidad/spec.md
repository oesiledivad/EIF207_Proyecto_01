# Feature Specification: Verificación de resolubilidad de la cripta

**Feature Branch**: `kyara`

**Created**: 2026-11-15

**Status**: Draft

**Input**: User description: "Verificación de resolubilidad de la cripta (Cripta Parte II, §3.5 y §5.4): determinar antes de iniciar una partida si la cripta puede ganarse, entregar un orden de obtención de llaves o un reporte de bloqueo, e integrarlo con la interfaz y las banderas --verificar, --forzar y --bench."

## Clarifications

### Session 2026-11-15

- Q: Cuando la cripta es resoluble, ¿el orden de obtención de llaves debe incluir todas las llaves obtenibles o solo las necesarias para ganar? → A: Todas las llaves obtenibles desde la sala inicial.
- Q: Cuando la cripta no es resoluble y existen varios ciclos de dependencias, ¿el reporte debe mostrar solo uno o todos? → A: Todos los ciclos distintos, cada uno iniciando en su llave de menor id y ordenados por ese id.
- Q: Si una misma llave aparece publicada en varias ubicaciones, ¿qué debe hacer la verificación? → A: Considerarla obtenible en cualquiera de sus ubicaciones alcanzables; para el orden y el reporte se usa la alcanzable primero, con empate por menor id de sala.
- Q: Si la ubicación de las llaves no está disponible, ¿la partida debe iniciar o no? → A: La partida DEBE iniciar con el aviso "resolubilidad no verificada" y sin ningún veredicto.
- Q: Con --verificar, ¿qué código de salida debe devolver el programa? → A: 0 si es resoluble, 1 si no es resoluble, 2 si la ubicación de llaves no está disponible o hay un error de uso.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saber si una cripta se puede ganar y en qué orden obtener las llaves (Priority: P1)

Antes de iniciar una partida, el jugador (o quien prueba el juego) quiere saber si la cripta elegida puede ganarse. Si puede, el programa entrega un orden de obtención que incluye todas las llaves obtenibles de la cripta, en el que cada llave aparece después de todas las llaves necesarias para alcanzarla.

**Why this priority**: Es el núcleo de la capacidad. Sin este veredicto no existen ni el reporte de bloqueo ni la decisión de iniciar o no la partida.

**Independent Test**: Se verifica una cripta resoluble conocida y se comprueba que el veredicto es "resoluble" y que el orden de llaves respeta las dependencias, sin abrir la interfaz.

**Acceptance Scenarios**:

1. **Given** una cripta resoluble cuya única llave es llave_salida y está al alcance desde la sala inicial, **When** se verifica, **Then** el veredicto es resoluble y el orden contiene únicamente llave_salida.
2. **Given** una cripta resoluble con varias llaves encadenadas (cada llave detrás de una puerta que exige la anterior), **When** se verifica, **Then** el orden entregado incluye todas las llaves obtenibles, coloca cada llave después de todas las llaves necesarias para alcanzarla e incluye llave_salida.
3. **Given** una cripta resoluble con una llave obtenible que no es necesaria para ganar, **When** se verifica, **Then** el orden incluye también esa llave.
4. **Given** una cripta con varios órdenes válidos de obtención de llaves, **When** se verifica dos veces, **Then** ambas ejecuciones producen exactamente el mismo orden.
5. **Given** una llave que suelta un enemigo errante, **When** se verifica, **Then** la llave se ubica en la sala donde ese enemigo inicia y se considera obtenible allí.

---

### User Story 2 - Entender por qué una cripta no se puede ganar (Priority: P1)

Cuando la cripta no es resoluble, el jugador necesita un reporte que explique el bloqueo: qué llaves no pueden obtenerse, qué puertas cerradas frenan el avance, dónde están esas llaves y, si existe, el ciclo de dependencias que lo causa.

**Why this priority**: Un veredicto negativo sin explicación no permite corregir la cripta ni entender por qué la partida no inicia.

**Independent Test**: Se verifica una cripta con llave_salida detrás de la única puerta que ella misma abre y se comprueba que el reporte lista la llave inalcanzable, la puerta bloqueada, su ubicación y el ciclo.

**Acceptance Scenarios**:

1. **Given** una cripta cuya llave_salida está detrás de la única puerta que ella misma abre, **When** se verifica, **Then** el veredicto es no resoluble y el reporte señala el ciclo de esa llave consigo misma.
2. **Given** una cripta con dos llaves A y B donde A está detrás de una puerta que requiere B y B detrás de una puerta que requiere A, **When** se verifica, **Then** el reporte señala el ciclo de dos llaves e indica las puertas y salas involucradas.
3. **Given** una cripta no resoluble, **When** se verifica, **Then** el reporte incluye las llaves que no pueden obtenerse, las puertas cerradas adyacentes a la región alcanzable con la llave que requiere cada una, y para cada una de esas llaves su sala y, si la suelta un enemigo, el id de esa instancia de enemigo.
4. **Given** una cripta no resoluble con un ciclo, **When** se verifica dos veces, **Then** ambas ejecuciones reportan el mismo ciclo, con el mismo punto de partida y el mismo sentido.
5. **Given** una cripta no resoluble con varios ciclos distintos, **When** se verifica, **Then** el reporte lista todos los ciclos, cada uno iniciando en su llave de menor id y recorrido en el mismo sentido, ordenados por ese id de inicio.

---

### User Story 3 - Impedir iniciar partidas imposibles, con opción de forzar (Priority: P2)

Al iniciar una partida, la interfaz muestra el resultado de la verificación. Si la cripta no es resoluble, la partida no inicia y se muestra el reporte, salvo que el programa se haya ejecutado con la bandera --forzar.

**Why this priority**: Conecta la verificación con la experiencia de juego y evita que el jugador pierda tiempo en una cripta imposible.

**Independent Test**: Se arranca el programa con una cripta no resoluble, primero sin --forzar y luego con --forzar, y se observa que solo en el segundo caso la partida inicia.

**Acceptance Scenarios**:

1. **Given** una cripta no resoluble y el programa ejecutado sin --forzar, **When** se intenta iniciar la partida, **Then** la partida no inicia y se muestra el reporte de bloqueo.
2. **Given** una cripta no resoluble y el programa ejecutado con --forzar, **When** se intenta iniciar la partida, **Then** la partida inicia y el reporte sigue disponible para el jugador.
3. **Given** una cripta resoluble, **When** se inicia la partida, **Then** la interfaz muestra el resultado de la verificación y la partida inicia sin intervención adicional.
4. **Given** una cripta cuya ubicación de llaves no está disponible (sin red y sin información guardada válida), **When** se intenta iniciar la partida, **Then** la partida inicia con el aviso "resolubilidad no verificada" y no se muestra ningún veredicto, con o sin --forzar.

---

### User Story 4 - Verificar desde consola sin abrir la interfaz (Priority: P2)

Quien desarrolla o prueba quiere ejecutar solo la verificación de una cripta e imprimir el resultado en consola, sin abrir la ventana del juego, con o sin conexión.

**Why this priority**: Permite automatizar pruebas y revisar criptas rápidamente.

**Independent Test**: Se ejecuta el programa con --verificar sobre una cripta y se comprueba que imprime el resultado y termina sin abrir ninguna ventana; se repite con --offline.

**Acceptance Scenarios**:

1. **Given** el programa ejecutado con --verificar y el nombre de una cripta, **When** termina la verificación, **Then** el resultado se imprime en consola y no se abre la interfaz.
2. **Given** el programa ejecutado con --verificar junto con --offline, **When** termina la verificación, **Then** el resultado se imprime en consola, sin interfaz y sin solicitudes de red.
3. **Given** el programa ejecutado con --verificar, **When** termina, **Then** el código de salida es 0 si la cripta es resoluble, 1 si no es resoluble y 2 si la ubicación de llaves no está disponible o hay un error de uso.

---

### User Story 5 - Reutilizar la ubicación de llaves sin repetir solicitudes (Priority: P3)

La ubicación de las llaves se obtiene del servicio y cuenta dentro del presupuesto de solicitudes de la cripta. Si ya se obtuvo para la misma versión de la cripta, se reutiliza sin consultar de nuevo.

**Why this priority**: Protege el presupuesto de red, pero el veredicto puede obtenerse sin esta optimización.

**Independent Test**: Se verifica dos veces la misma versión de una cripta y se comprueba que la segunda verificación no realiza ninguna solicitud de red para las llaves.

**Acceptance Scenarios**:

1. **Given** una verificación previa cuya ubicación de llaves quedó guardada, **When** se verifica de nuevo con la misma versión de la cripta, **Then** no se realiza ninguna solicitud de red para la ubicación de llaves.
2. **Given** una ubicación de llaves guardada de una versión anterior, **When** se verifica una versión distinta de la cripta, **Then** la información guardada no se reutiliza y se consulta de nuevo.
3. **Given** una verificación que requiere consultar la ubicación de llaves, **When** se realiza la consulta, **Then** esa solicitud queda contada dentro del presupuesto de solicitudes de la cripta.

---

### User Story 6 - Medir el rendimiento frente a la alternativa ingenua (Priority: P3)

Quien evalúa el proyecto quiere evidencia medida de que la verificación escala de forma aproximadamente lineal y supera a la alternativa ingenua de repetir la exploración completa cada vez que se obtiene una llave.

**Why this priority**: Es evidencia exigida por la constitución, pero depende de que el veredicto ya funcione.

**Independent Test**: Se ejecuta el modo --bench con una semilla y se comprueba que reporta tiempos de ambas alternativas sobre criptas sintéticas con muchas llaves encadenadas, y que la misma semilla produce las mismas criptas.

**Acceptance Scenarios**:

1. **Given** el modo --bench con una semilla, **When** se ejecuta, **Then** se miden la verificación y la alternativa ingenua sobre criptas sintéticas de muchas llaves encadenadas y se imprimen ambos tiempos.
2. **Given** el modo --bench ejecutado dos veces con la misma semilla, **When** se comparan, **Then** las criptas sintéticas generadas son idénticas.
3. **Given** criptas sintéticas de tamaños crecientes, **When** se mide la verificación, **Then** el tiempo total crece de forma aproximadamente lineal con la cantidad de salas, salidas y llaves.

---

### Edge Cases

- La llave_salida está en la sala inicial: el orden la incluye junto con las demás llaves obtenibles de la cripta; si es la única llave obtenible, el orden contiene solo esa llave.
- Una llave no obtenible en una cripta resoluble: NO aparece en el orden.
- Una llave que suelta un enemigo está en una región que solo se alcanza con otra llave: se trata igual que cualquier llave de esa región.
- Obtener una llave vuelve alcanzable una región completa con varias llaves más: todas se consideran obtenibles sin repetir la exploración de la cripta.
- llave_salida es inalcanzable aunque la puerta que la requiere y lleva a sala_salida existe: no resoluble.
- llave_salida es obtenible pero ninguna puerta que la requiere conduce a sala_salida: no resoluble.
- Varias puertas cerradas exigen la misma llave: todas se abren al obtenerla.
- Ubicación de llaves no disponible (sin red y sin información guardada para esa versión): el programa lo informa y no emite un veredicto falso. La partida inicia mostrando el aviso "resolubilidad no verificada", con o sin --forzar.
- Una misma llave publicada en varias ubicaciones: DEBE considerarse obtenible en cualquiera de ellas que sea alcanzable. Para el orden y el reporte se usa la ubicación alcanzable primero, con empate por menor id de sala. Si ninguna es alcanzable, el reporte DEBE listar todas sus ubicaciones.
- Una llave sin ubicación publicada por el servicio: se informa como dato faltante y no se asume su sala.
- Trampas o cierres automáticos: no cambian el veredicto, porque la puerta puede reabrirse con la misma llave.
- Empates en el orden de llaves, en el punto de inicio de un ciclo o en el orden entre ciclos: se resuelven con una regla explícita y estable (menor id).
- Varios ciclos encontrados por la exploración: el reporte los incluye todos, sin omitir ninguno.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El programa DEBE determinar, antes de iniciar una partida, si la cripta puede ganarse, usando solo las salas, las salidas, las puertas cerradas con la llave que requiere cada una, y la ubicación de las llaves publicada por el servicio para esa cripta.
- **FR-002**: La ubicación de cada llave DEBE incluir su sala y, si la suelta un enemigo, el id de esa instancia de enemigo. Una llave PUEDE tener varias ubicaciones publicadas, y la llave se considera obtenible si al menos una es alcanzable.
- **FR-003**: La verificación DEBE asumir que el jugador atraviesa toda salida abierta y toda salida cerrada cuya llave ya obtuvo, que las llaves no se consumen y que todo enemigo puede ser derrotado.
- **FR-004**: Una llave que suelta un enemigo DEBE considerarse obtenible en la sala donde ese enemigo inicia.
- **FR-005**: La verificación NO DEBE tratar las trampas ni los cierres automáticos como bloqueos.
- **FR-006**: Una cripta DEBE considerarse resoluble si, partiendo de la sala inicial y bajo los supuestos anteriores, el jugador puede obtener llave_salida y llegar a sala_salida a través de una puerta que la requiere.
- **FR-007**: Si la cripta es resoluble, el resultado DEBE incluir un orden de obtención que contenga todas las llaves obtenibles desde la sala inicial, en el que cada llave aparece después de todas las llaves necesarias para alcanzarla. El orden NO DEBE incluir llaves que no sean obtenibles.
- **FR-008**: El orden de llaves DEBE ser determinista: la misma cripta DEBE producir siempre el mismo orden, y los empates DEBEN resolverse con una regla explícita y estable.
- **FR-009**: Si la cripta no es resoluble, el resultado DEBE incluir un reporte con las llaves que no pueden obtenerse.
- **FR-010**: El reporte DEBE incluir las puertas de la frontera bloqueada (puertas cerradas adyacentes a la región alcanzable) con la llave que requiere cada una.
- **FR-011**: El reporte DEBE indicar, para cada llave de la frontera bloqueada, su sala y, si aplica, el id del enemigo que la suelta. Si la llave tiene varias ubicaciones, el reporte DEBE listarlas todas.
- **FR-012**: Si una llave está detrás de puertas que solo ella abre, directamente o mediante una cadena de llaves, el reporte DEBE indicar el ciclo concreto. Un ciclo es una cadena de llaves encontrada por la misma exploración en la que cada llave está detrás de una puerta que requiere la siguiente y la última está detrás de una puerta que requiere la primera. Si la exploración encuentra varios ciclos distintos, el reporte DEBE incluirlos todos y NO DEBE omitir ninguno; no se exige enumerar todas las combinaciones posibles de rutas alternativas.
- **FR-013**: Los ciclos reportados DEBEN ser deterministas: la misma cripta DEBE producir siempre los mismos ciclos, cada uno con el mismo punto de partida (su llave de menor id) y el mismo sentido, y la lista de ciclos DEBE ordenarse por el id de ese punto de partida.
- **FR-014**: Al iniciar una partida, la interfaz DEBE mostrar el resultado de la verificación.
- **FR-015**: Si la cripta no es resoluble y el programa no se ejecutó con --forzar, la partida NO DEBE iniciar y DEBE mostrarse el reporte.
- **FR-016**: Si el programa se ejecutó con --forzar, la partida DEBE iniciar aunque la cripta no sea resoluble.
- **FR-017**: La bandera --verificar seguida de una cripta DEBE ejecutar únicamente la verificación e imprimir el resultado en consola, sin abrir la interfaz.
- **FR-018**: La bandera --verificar DEBE funcionar también junto con --offline.
- **FR-018a**: Con --verificar, el programa DEBE terminar con código de salida 0 si la cripta es resoluble, 1 si no es resoluble y 2 si la ubicación de llaves no está disponible o hay un error de uso. NO DEBE devolver 0 cuando la cripta no es resoluble ni cuando no hay veredicto.
- **FR-019**: La consulta de la ubicación de llaves DEBE contarse dentro del presupuesto de solicitudes de la cripta.
- **FR-020**: La respuesta con la ubicación de llaves DEBE poder guardarse y reutilizarse mientras coincida la versión de la cripta; con la misma versión NO DEBE realizarse una nueva solicitud de red.
- **FR-021**: Si la versión de la cripta no coincide con la información guardada, esta NO DEBE reutilizarse.
- **FR-022**: Si la ubicación de llaves no está disponible (sin red y sin información guardada válida), el programa DEBE informarlo y NO DEBE emitir un veredicto de resolubilidad. En una partida normal, la partida DEBE iniciar mostrando el aviso "resolubilidad no verificada", sin depender de --forzar, y NO DEBE mostrar ni resoluble ni no resoluble.
- **FR-023**: La verificación de la cripta publicada más grande DEBE tardar menos de 200 ms en el equipo local, sin contar red.
- **FR-024**: El costo total de la verificación DEBE crecer aproximadamente de forma lineal con la cantidad de salas, salidas y llaves; NO DEBE repetirse la exploración completa de la cripta cada vez que se obtiene una llave.
- **FR-025**: La frontera bloqueada y las dependencias entre llaves DEBEN obtenerse de la misma exploración que decide la resolubilidad, sin exploraciones adicionales por cada llave.
- **FR-026**: El modo --bench DEBE medir la verificación contra la alternativa ingenua de repetir la exploración por cada llave, usando criptas sintéticas de muchas llaves encadenadas, deterministas por semilla.
- **FR-027**: La verificación NO DEBE simular combate, tiempo, trampas ni movimiento de enemigos, NO DEBE modificar el estado del juego y NO DEBE reportar la ruta concreta del jugador, solo el orden de llaves.
- **FR-028**: Los modos --verificar y --bench NO DEBEN abrir la interfaz.
- **FR-029**: La verificación NO DEBE contener datos de una cripta concreta; todo dato DEBE provenir del servicio o de los datos sin conexión.

### Key Entities

- **Cripta**: conjunto de salas conectadas por salidas; declara sala_inicial, sala_salida y llave_salida, y tiene una versión.
- **Sala**: lugar de la cripta; puede contener llaves y ser el punto de inicio de enemigos.
- **Salida**: conexión entre dos salas; puede estar abierta o ser una puerta cerrada que requiere una llave.
- **Llave**: objeto que abre todas las puertas que la requieren; se ubica en una sala y puede ser soltada por una instancia de enemigo.
- **Instancia de enemigo**: enemigo identificado por un id, que inicia en una sala y puede soltar una llave.
- **Resultado de verificación**: veredicto de resolubilidad junto con el orden de llaves (si es resoluble) o el reporte de bloqueo (si no lo es).
- **Reporte de bloqueo**: llaves inalcanzables, puertas de la frontera bloqueada con su llave requerida, ubicación de esas llaves y ciclo de dependencias si existe.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los escenarios del Apéndice B (ciclo de la llave de salida, llave de enemigo errante, orden determinista, partida bloqueada sin --forzar) se cumplen en pruebas automatizadas.
- **SC-002**: Dos verificaciones consecutivas de la misma cripta producen resultados idénticos (orden de llaves, frontera y ciclo) en el 100% de los casos probados.
- **SC-003**: La verificación de la cripta publicada más grande tarda menos de 200 ms en el equipo local, sin contar red.
- **SC-004**: Al multiplicar por 10 el tamaño de una cripta sintética, el tiempo de verificación crece menos de 15 veces, y en criptas con muchas llaves encadenadas es menor que el de la alternativa ingenua.
- **SC-005**: Con la misma versión de cripta, la segunda verificación realiza 0 solicitudes de red para la ubicación de llaves.
- **SC-006**: Con --verificar, el resultado aparece en consola y 0 ventanas de la interfaz se abren, con y sin --offline.
- **SC-007**: Ante una cripta no resoluble sin --forzar, 0 partidas inician y el jugador ve el reporte con al menos una puerta bloqueada y la llave que requiere.

## Assumptions

- La cripta publicada más grande y su ubicación de llaves se obtienen del servicio o de los datos sin conexión; la verificación no depende de ningún dato fijo en el código.
- "Región alcanzable" es el conjunto de salas a las que el jugador puede llegar bajo los supuestos de la verificación con las llaves ya obtenibles.
- Cuando existen varias puertas de frontera, varias llaves inalcanzables o varios ciclos posibles, el reporte DEBE listarlos todos con orden estable por id; cada ciclo comienza con su menor id.
- La interfaz muestra el resultado en texto; su diseño visual queda fuera de esta spec.
- La verificación solo consulta información; el estado del juego no cambia.
- Dependencia: el servicio web publica el esqueleto y la ubicación de llaves de cada cripta, con su versión.
- Fuera de alcance: simulación de combate, tiempo, trampas, movimiento de enemigos y la ruta concreta del jugador.
- La verificación se ejecuta al iniciar una partida nueva y con --verificar; no se ejecuta al continuar una partida guardada ni en --replay, porque esas partidas ya iniciaron.
- Los ids de llave se comparan como cadenas, carácter por carácter (orden lexicográfico; por ejemplo, itm_llave_10 va antes que itm_llave_2); los ids de sala se comparan como enteros.

## Cierre de entrega: diagnóstico y datos reproducibles (17/11/2026)

- **FR-030**: Cada intento HTTP DEBE dejar un registro de diagnóstico con fecha, recurso, número de intento, resultado HTTP o error de transporte, duración y solicitudes usadas/presupuesto. Los rechazos por presupuesto y la espera por 429 DEBEN distinguirse. El registro NO DEBE modificar el reloj virtual ni añadir solicitudes; DEBE mantenerse separado del replay y admitir rotación para limitar el disco.
- **FR-031**: La entrega DEBE incluir un paquete separado de datos actuales con versiones, esqueleto completo, contenido, fichas y ubicación de llaves. Actualizarlo NO DEBE sobrescribir el paquete histórico que usa el replay de ejemplo. La descarga DEBE respetar lotes y presupuesto y rechazar una captura si las versiones cambian durante ella.

Aceptación: un 429 seguido de 200 deja dos intentos y una espera; un fallo de transporte queda registrado; un rechazo previo al envío no incrementa solicitudes. Desde una caché vacía, la verificación offline del paquete actual emite veredicto sin red; el replay histórico sigue funcionando.
