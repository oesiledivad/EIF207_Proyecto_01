# Investigación: Niebla de guerra y viaje automático «ir a»

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Cada decisión indica su razón, sus alternativas y su complejidad. Las mediciones K1 a K9 se
definen en el plan y las produce `--bench`. Donde dice «a confirmar» remite a un punto C del plan.

Notación: S = salas de la cripta, X = salas exploradas, E = salidas (como máximo 4 por sala),
r = salas reveladas por una acción, c = cambios de una acción.

---

## D1. Estado de sala para el jugador

**Decisión**: una `list[int]` de tamaño `max_id + 1`, indexada por id de sala, con 0 desconocida,
1 avistada y 2 explorada. Es la misma idea de direccionamiento directo de `IndiceSalas`: los ids
son enteros pequeños y secuenciales.

**Razón**: consultar es `lista[id]`, O(1) sin hash (FR-035). Cambiar un estado es una asignación.
Los tres estados caben en un entero pequeño, lo que además hace trivial serializarlos.

**Alternativas**:

- Dos listas booleanas (explorada, avistada): permite el estado imposible «explorada y no
  avistada» o ambas falsas con significados distintos; un solo entero lo evita.
- Atributo `estado_jugador` dentro de `SalaJuego`: mezcla conocimiento del jugador con la entidad
  de dominio, y obliga a recorrer salas para exportar el conocimiento. Se descarta por separación
  y por serialización.
- Lista de ids explorados con búsqueda lineal: consulta O(X). Se mide como alternativa en K1.
- `dict` o `set`: prohibidos por el principio I.

**Complejidad**: consulta O(1); marcar explorada O(4) (revisa sus salidas para avistar destinos).

---

## D2. Memoria de puertas

**Decisión**: una `list[int]` plana de tamaño `4 * (max_id + 1)`. La posición de la salida
`direccion` de la sala `s` es `s * 4 + i`, con `i` = N 0, S 1, E 2, O 3. Valores: 0 sin observar,
1 abierta, 2 cerrada. La posición (la «clave») se calcula una vez al ensamblar las salas y se
guarda en la propia `SalidaSimple`.

**Razón**: en los datos cada puerta cerrada se declara solo en un lado y la inversa está abierta,
así que cada salida dirigida tiene su propio estado y su propia memoria. Una lista plana mantiene
la consulta en O(1) y es compacta (un byte por salida al serializar). Guardar la clave en la salida
evita convertir dirección a índice en cada consulta; la conversión se hace con una comparación
explícita, sin `dict`.

**Alternativas**:

- Lista de listas por sala (4 elementos): una indirección más y más objetos; sin ventaja.
- Memoria como atributo `recordada` de `SalidaSimple`: más simple de escribir, pero el cambio se
  haría con `cambiar(salida, "recordada", ...)`, que sí es invertible hoy. Se descarta porque
  esparce el conocimiento por objetos de dominio y complica exportar e importar el conocimiento
  completo para la spec 004. Se mantiene como alternativa viable si D5 resultara inviable.
- Una sola memoria por pareja de salas conectadas: es incorrecto, porque la salida de ida y la de
  vuelta tienen estados distintos.

**Complejidad**: consulta O(1); observar la sala actual cuesta O(4 + entrantes de la sala).

---

## D3. Salidas entrantes

**Decisión**: una `list` de tamaño `max_id + 1` cuyo elemento `v` es la lista de `SalidaSimple`
que llegan a `v`. Se construye una sola vez al ensamblar las salas, recorriendo las salidas de
todas las salas.

**Razón**: hace falta en dos sitios. Primero, para observar: estando en `v`, el jugador observa
también las salidas de otras salas que entran a `v`. Segundo, para el Dijkstra inverso: las aristas
que llegan a una sala son las que se relajan. Construirla cuesta O(E) una vez; usarla cuesta lo
que tiene cada sala.

**Alternativas**:

- Recorrer todas las salas para hallar las que apuntan a `v`: O(S) por consulta; inaceptable
  para el paso de «ir a» y para la observación en cada acción.
- Calcular entrantes bajo demanda por sala con caché: añade invalidación sin ganar nada, porque el
  esqueleto no cambia durante la partida.
- Dijkstra directo (desde el origen) que solo usa salidas, sin entrantes: ver D7; evita la lista
  pero pierde la regla natural de desempate.

**Complejidad**: construcción O(E) una vez; memoria O(E).

---

## D4. Cuándo se observan las puertas

**Decisión**: la observación ocurre una vez por acción, al final de `consumir_tiempo` y antes de
`finalizar`, dentro del intervalo del historial. Observa las 4 salidas de la sala actual y sus
entrantes, y asigna a la memoria el estado real. El estado de sala (entrar, antorcha) se actualiza
en `_ejecutar_movimiento`, apenas el jugador cambia de sala.

**Razón**: FR-008 pide que mientras el jugador permanece en una sala los cambios se reflejen «en el
momento». Durante una acción el jugador no cambia de sala mientras corren los eventos, y la
memoria guarda solo el último estado (caso límite «una puerta cambia dos veces»). Por tanto
observar al final de la acción produce exactamente el mismo estado final que observar en cada
cambio. Evita enganchar `Puertas.abrir_salida` y `procesar_cierre_puerta`, que no conocen el origen
de la salida ni al jugador.

**Alternativas**:

- Gancho por cambio de puerta (notificar al conocimiento desde `abrir_salida` y
  `procesar_cierre_puerta`): fiel al texto «en el momento», pero acopla `Puertas` al conocimiento y
  necesita saber en qué sala está el jugador en cada evento; más superficie de error. Se conserva
  como plan B si una prueba mostrara una diferencia observable.
- Observar al inicio de la acción además del final: redundante; si el estado no cambió, la
  asignación se omite sin registrar nada.
- Observar también tras un retroceso: PROHIBIDO, porque `usar_pergamino` corre fuera de un
  intervalo y el cambio no sería invertible; el retroceso ya restaura la memoria.

**Complejidad**: O(4 + entrantes) por acción; cada cambio real cuesta O(1).

**Riesgo**: bajo. Cubierto por pruebas de las historias 2 y 4 (puerta que cambia estando en
cualquiera de las dos salas).

---

## D5. Registro de los cambios en el historial

**Decisión**: agregar `Historial_Retroceso.asignar(lista, posicion, valor)`, que registra
`lista_asignada` con `[lista, posicion, valor_anterior]` y asigna; no registra si el valor no
cambia. `GestorPartida._aplicar_reversion` se amplía para invertir ese caso. Cada cambio se anexa
además al registro cronológico del conocimiento con `historial.agregar(registro, cambio)`, que ya
existe (`lista_agregada`).

**Razón**: el historial actual solo invierte atributos de un objeto, y agregar o quitar elementos de
una lista. Asignar una posición no está cubierto, y es la operación natural de D1 y D2. Con el tipo
nuevo cada cambio cuesta O(1) al registrar y al invertir (FR-037), y la antorcha produce a lo sumo
unos 16 cambios por entrada.

**Alternativas**:

- Una celda por posición (objeto con un atributo `valor`) para usar `cambiar` sin tocar el
  historial: 5 objetos por sala, más memoria y más recorridos; se mide la diferencia en K3.
- Copiar el conocimiento completo por acción: O(S) por acción y viola FR-037; K3 lo muestra.
- Guardar una diferencia calculada al cerrar el intervalo (comparar contra una copia): O(S) por
  acción.
- Reconstruir el conocimiento desde el registro al revertir: más lento y innecesario.

**Complejidad**: registrar O(1); invertir O(c).

**A confirmar (C8)**: que `lista_agregada` se invierte quitando el último elemento (`pop()`); si usa
`remove` o `index` recorre el registro entero y rompe FR-037 en partidas largas.

---

## D6. Costo de salida

**Decisión**: `SalidaSimple` gana `costo: int = 100`, y `SalidaVecina` también. `parsear_sala` lee
el campo `costo` de cada salida del esqueleto y usa 100 si no está. `Salidas.agregar` recibe el costo
como último parámetro opcional, por lo que las llamadas existentes (incluidas las de `bench`) no
cambian.

**Razón**: FR-023 pide minimizar el costo total y que una salida sin costo valga 100. El tiempo que
consume moverse según el costo lo implementa la spec 003; aquí el costo solo se lee para las rutas.

**Alternativas**:

- Tabla de costos separada indexada por clave de salida: otra lista paralela sin beneficio, porque
  el costo se lee junto con la salida.
- Calcular el costo en el momento del paso desde el DTO: el DTO del esqueleto no se conserva
  después de ensamblar.

**A confirmar (C1)**: se supone costo mayor que cero. Con costo cero la regla «elegir la vecina con
costo más distancia mínimos» podría girar entre dos salas de igual distancia. Defensa en dos capas:
normalizar el costo menor que 1 a 100 al parsear, y cortar el viaje a tantos pasos como salas
exploradas (motivo `sin_ruta`).

---

## D7. Algoritmo de «ir a»

**Decisión**: Dijkstra inverso. Se parte del destino con distancia 0 y se relajan las aristas
entrantes. Una arista `u -> v` solo se usa si `u` está explorada y la memoria de la salida de `u` es
«abierta». La búsqueda se detiene al fijar la sala actual. El paso elige, entre las salidas de la
sala actual usables y con destino explorado, la que minimiza `costo + distancia[destino]`; desempata
por menor id de sala destino y luego por índice de dirección (N, S, E, O). Se recalcula antes de
cada paso con el conocimiento vigente.

**Razón**:

- Una sola ejecución da la distancia de todas las salas hacia el destino, y el desempate «menor id
  de la vecina» es natural: se comparan solo las vecinas de la sala actual. Es la misma regla del
  cazador.
- Con costos positivos, todo candidato de costo mínimo tiene distancia estrictamente menor que la
  sala actual, de modo que ya está fijado cuando se fija la sala actual. La parada anticipada no
  pierde empates.
- Reglas de la spec cubiertas: solo salas exploradas y salidas recordadas abiertas (FR-022); mínimo
  costo y no mínimo de saltos (FR-023); desempate (FR-024); no abre puertas (FR-032).
- Recalcular en cada paso es lo que exige FR-026, porque la memoria cambia al observar. El costo es
  pequeño porque el subgrafo es solo lo explorado.
- Estructuras auxiliares sin `set`: dos listas de tamaño S (distancia y marca de generación). Un
  contador de generación evita reinicializar S posiciones en cada paso.

**Alternativas**:

- **Dijkstra desde el origen** con padres: da una ruta, pero el desempate por menor id del primer
  paso exige propagar una clave secundaria («primer paso») en cada relajación; más delicado para el
  mismo costo asintótico. Se mide en K6.
- **Reutilizar distancias entre pasos**: la memoria de puertas cambia al observar la sala nueva, y
  una puerta recordada abierta que resulta cerrada invalida distancias de forma no local. Mantener
  la corrección exige detectar qué distancias dependen de la arista cambiada, con más código que el
  recálculo. Se mide en K6 y solo se adopta si gana por más de 2 veces.
- **BFS con la cola de la spec 001**: correcto solo con costos iguales; FR-023 prefiere menor costo
  aunque tenga más salas. K8 muestra rutas peores.
- **Floyd-Warshall o precálculo de todas las distancias**: O(X^3) o memoria O(X^2); además se
  invalida con cada puerta.
- **A\***: no hay coordenadas en los datos para una heurística admisible.
- **Selección lineal del mínimo (Dijkstra O(V^2))**: sin montículo; se mide en K7 y se descarta
  para X grande.

**Complejidad**: O((X + E_x) log X) por paso, con E_x las salidas usables entre salas exploradas
(a lo sumo 4X). Con parada anticipada el trabajo real es el del disco de radio igual a la distancia
a la sala actual.

---

## D8. Montículo mínimo propio y genérico

**Decisión**: `estructuras/Monticulo_Minimo.py`, con tres listas paralelas (prioridad, desempate,
elemento) y comparación lexicográfica por `(prioridad, desempate)`. Operaciones: `insertar`,
`extraer_minimo`, `esta_vacio`, `vaciar`. La eliminación es perezosa: el llamador reinserta con
mejor prioridad y descarta las entradas obsoletas al extraer.

**Razón**: la búsqueda del cazador (spec 003) también lo necesita, así que el elemento es opaco y las
prioridades son enteros, con desempate explícito (principio II). Las listas paralelas evitan crear
un objeto por entrada. La eliminación perezosa es más simple que mantener el índice de cada
elemento y suficiente porque el grafo tiene grado máximo 4.

**Alternativas**:

- **Reutilizar `HeapAgendaEventos`**: está atado a `Evento`, a `indice` por evento y al historial
  (`registrar`). Generalizarlo arriesga romper la agenda que la Parte I ya valida. Decisión: NO
  se toca; una refactorización futura podría hacer que la agenda use el montículo genérico.
- **Montículo con decremento de clave e índice por elemento**: menos entradas en el montículo, más
  código y más estado; se mide en K7.
- **Montículo con comparador (callable) genérico**: más flexible, pero una llamada de Python por
  comparación encarece cada paso; con prioridades enteras y desempate entero no se necesita.
- **`heapq`**: prohibido.

**Complejidad**: insertar y extraer O(log n); n es a lo sumo el número de relajaciones, O(4X).

---

## D9. ¿«Ir a» y el cazador comparten la búsqueda? (§5.3)

**Decisión**: se comparten tres piezas y se separa una.

- Compartido: `MonticuloMinimo` (D8), la regla de desempate (menor id de la sala vecina, luego
  índice de dirección) y el módulo `modelo/Rutas.py`, que ofrece
  `distancias_hacia(destino, usable, parar_en)` y `elegir_paso(origen)`. El predicado
  `usable(salida)` lo aporta cada llamador.
- Separado: qué salidas son usables. «Ir a» pasa un predicado sobre el conocimiento del jugador
  (salas exploradas, salidas recordadas abiertas). El cazador conoce el mapa completo, así que
  pasará un predicado sobre el estado real.

**Razón**: el problema de fondo es el mismo (distancia mínima hacia un objetivo y elección del paso
con desempate), y duplicar el algoritmo invita a que las dos reglas de desempate diverjan; la spec
exige que sean la misma. Lo que cambia entre ambos es el subgrafo visible, y eso es justo lo que
parametriza el predicado. Separar las implementaciones se justificaría si el cazador necesitara
costos dinámicos o rutas con puertas que se abren; eso lo decide la spec 003.

**Alternativas**:

- **Dos implementaciones independientes**: cada una puede especializarse (el cazador sin filtrar
  por exploración), pero se duplica la regla de desempate y el riesgo de divergencia.
- **Que «ir a» llame al cazador, o al revés**: acopla un comando del jugador a un enemigo.
- **Predicado como arreglo precalculado**: evita llamadas, pero cuesta O(E) por paso. Se mide: si la
  llamada al predicado domina, se pasa un arreglo de banderas por clave de salida.

**Costo de compartir**: una llamada de predicado por arista relajada; se acota en K5 y K6. **A
confirmar (C11)** en el plan de la spec 003.

---

## D10. Viaje: quién lo ejecuta y cómo pasa por el flujo de acción

**Decisión**: `ViajeControlador` guarda el destino y el estado del viaje, y expone `iniciar(destino)`,
`avanzar()` y `cancelar()`. Cada llamada a `avanzar` hace exactamente un paso:

1. Recalcula la distancia y elige el paso con el conocimiento vigente. Si no hay paso, se detiene
   con `sin_ruta` sin consumir tiempo (FR-030).
2. Ejecuta `Aplicacion.mover(direccion)`, que pasa por `_accion_jugador`, la plantilla común: carga
   del destino, intervalo del historial, trampas, eventos, `partida.log`, victoria y derrota.
3. Con el resultado, decide si se detiene: partida terminada, daño (la vida del jugador baja
   respecto de antes del paso, lo que cubre ataque, trampa y veneno), entrada a sala con enemigos
   vivos (bandera fijada en la entrada por `_ejecutar_movimiento`) o llegada al destino.

Si el viaje no se ha detenido, la vista llama otra vez a `avanzar` en su siguiente ciclo. Hay también
`ir_a_completo(destino)` que repite `avanzar` hasta detenerse, para pruebas y consola. Cualquier
otra acción del jugador, incluido el pergamino, cancela el viaje: `_accion_jugador` lo cancela si el
llamador no es el propio viaje.

**Razón**: FR-025 y FR-034 piden que cada paso sea una acción completa y que el pergamino revierta
solo el último paso sin continuar el viaje. Pasar por `mover` lo garantiza sin duplicar el ciclo.
Un paso por llamada deja a la vista libertad para pintar entre pasos y permite interrumpir.

**Alternativas**:

- **Bucle bloqueante dentro de la orden**: más simple, pero congela la interfaz, no deja
  interrumpir con el pergamino y complica la bitácora.
- **Encolar todos los pasos de la ruta calculada al inicio**: viola FR-026 (la ruta se recalcula
  antes de cada paso).
- **Registrar el viaje como una acción compuesta en el historial**: el pergamino revertiría todo el
  viaje, contra FR-034.
- **Detectar daño con un contador en el jugador**: más preciso (distingue daño 0), pero añade estado
  al modelo y al historial; la comparación de vida basta (C4).

**Complejidad**: un paso cuesta una acción normal más D7.

---

## D11. Registro en `partida.log` y reproducción

**Decisión**: la orden se escribe como la línea `# ir_a <sala>` antes del primer paso, y solo si la
orden fue aceptada. Cada paso se anexa como `["mover", "<dirección>"]` por el flujo normal. El
lector `leer_partida` omite toda línea cuyo texto, sin espacios iniciales, empiece por `#`; el
número de línea del mensaje de error sigue contando esas líneas. El reproductor ejecuta los
`mover` y llega al mismo estado final, porque el conocimiento es función de las acciones.

**Razón**: FR-033. La orden no debe ser una acción reproducible: sus pasos ya lo son, y reproducir
la orden recalcularía la ruta con riesgo de divergir. Un comentario es legible por humanos y permite
que el equipo agregue a mano líneas que citen el FR de un escenario (principio VII).

**Alternativas**:

- Nueva acción `ir_a` en `_validar_accion` que el reproductor ignore: mezcla datos y metadatos y
  obliga a tratar una acción sin efecto como acción.
- Un campo extra en la acción del paso (`["mover", "N", "ir_a"]`): rompe el formato `[accion,
  argumento]` de largo 2.
- No registrar la orden: se pierde la intención en la auditoría.
- Subir `formato` a 2: no hace falta, porque el cambio es una tolerancia de lectura, no una
  incompatibilidad con los registros existentes; se anota el efecto (un lector anterior rechaza el
  archivo) en [contracts/registro-partida.md](contracts/registro-partida.md).

**Complejidad**: una escritura por orden.

---

## D12. Qué muestra la vista

**Decisión**:

- El minimapa sigue dibujando la sala actual y sus vecinas en cruz, pero lee del conocimiento: el
  estado de la vecina (explorada o avistada), el costo de la salida y la puerta recordada (abierta,
  cerrada o sin observar). Nunca dibuja salas desconocidas.
- Un comando `mapa` muestra el mapa conocido completo como lista: salas exploradas con nombre,
  salidas, costo y puerta recordada, y salas avistadas solo con su id.
- La bitácora recibe un mensaje de categoría `viaje` con el motivo de cada detención.

**Razón**: FR-014 y FR-018. Los datos no traen coordenadas, así que dibujar el mapa completo exigiría
inventar una disposición. La lista cumple el requisito sin diseño visual, que está fuera de alcance.

**Alternativas**:

- Disposición en cuadrícula inferida desde las direcciones N, S, E, O: puede producir colisiones y
  contradicciones en criptas con salidas dirigidas; se pospone como mejora visual.
- Mostrar el mapa completo en un panel gráfico: diseño visual fuera de alcance.

---

## D13. Conocimiento serializable y reconstrucción (spec 004)

**Decisión**: el modelo ofrece una instantánea de enteros pequeños (formato, tamaño, estado de salas,
memoria de puertas), un registro cronológico de cambios `[tiempo, tipo, índice, valor]` y una
operación para reconstruir el estado tras los primeros `n` cambios del registro. Detalle en
[contracts/conocimiento-serializable.md](contracts/conocimiento-serializable.md).

**Razón**: FR-015 y FR-017. Una instantánea basta para guardar y restaurar; el registro permite a la
línea de tiempo reconstruir cualquier instante en O(n) sin conservar copias. El registro es una
lista que ya recibe el pergamino mediante `lista_agregada`, así que un retroceso lo recorta solo.

**Alternativas**:

- Serializar solo la instantánea y que la spec 004 reconstruya instantes pasados reproduciendo la
  partida: correcto pero lento y acopla la línea de tiempo al replay completo.
- Una instantánea por acción: O(S) por acción; viola la lógica de FR-037.
- Que el modelo decida el formato binario: es de la spec 004 y está fuera de alcance.

**A confirmar (C12)** con la spec 004: si prefiere clave por tiempo o por prefijo del registro.

---

## D14. Viaje y el estado del juego

**Decisión**: el estado del viaje (destino, activo, último motivo) NO es estado del juego: no se
guarda, no entra al historial y se cancela al retroceder, cargar o terminar. Lo único persistente
son sus pasos y el conocimiento.

**Razón**: FR-034 (el viaje no continúa tras el pergamino). Un viaje a medias al cargar una partida
sería ambiguo.

**Alternativas**: guardar el destino del viaje en el guardado: añade formato a la spec 004 sin
requisito que lo pida.

---

## D15. Fugas de información existentes

**Decisión**: `actualizar_vecindad` deja de copiar a la vista `tiene_enemigos` y `tiene_objetos` de
las vecinas, y `es_salida_final` se muestra solo para vecinas exploradas. El estado de la puerta de
la sala actual se sigue copiando porque el jugador la está observando.

**Razón**: FR-011 dice que explorar una vecina no revela su contenido; FR-014 pide que la vista
derive todo del conocimiento. Esta decisión cambia un comportamiento de la Parte I, por eso queda
como punto C7 a confirmar y con búsqueda explícita de pruebas afectadas en las tareas.

**Alternativas**: mantener los indicadores (incumple FR-011); distinguir «explorada entrando» de
«explorada por antorcha» para decidir cuándo mostrar contenido (agrega un cuarto estado que la spec
no tiene).

---

## Resumen de complejidad

| Operación | Costo | Requisito |
|-----------|-------|-----------|
| Estado de sala y puerta recordada | O(1) | FR-035 |
| Explorar al entrar | O(4), con antorcha O(16) | FR-036 |
| Observar puertas tras una acción | O(4 + entrantes) | FR-008 |
| Registrar un cambio / invertirlo | O(1) / O(1) | FR-037 |
| Un paso de «ir a» | O((X + E_x) log X) con parada anticipada | FR-038 |
| Mapa conocido completo (comando) | O(S) | FR-018 |
| Reconstruir tras `n` cambios | O(S + n) | FR-017 |
