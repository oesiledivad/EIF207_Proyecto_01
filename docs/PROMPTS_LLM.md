# Bitácora de uso de modelos de lenguaje (LLM)

Proyecto: Cripta — EIF 207 Estructuras de Datos — II Ciclo 2026.

Integrantes:

- Eliseo Zuñiga Obando.
- Fiorella Porras Mora.
- Kyara Rojas Gonzalez.

## Declaración general

Los LLM se utilizaron como apoyo para comprender conceptos, explorar alternativas, revisar código, generar casos de prueba, mejorar documentación y proponer implementaciones. Todo el código y texto entregado es responsabilidad del grupo.

## Registro cronológico de prompts

### Entrada #1

Fecha: 29/09/2026

Integrante: Fiorella Porras Mora.

Herramienta: ChatGPT — GPT-5.6 Luna.

Objetivo: Analizar y planificar la implementación de las funcionalidades asignadas, especialmente la agenda de eventos.

Prompt enviado:

> Este es mi proyecto, le pedí a claude que dividiera trabajo entre 3 personas y a mi me dijo que implementara estas funcionalidades, todas las estructuras de datos deben ser hechas a mano sin uso de librerías externas. funcionalidades: Fiorella — Motor de simulación y combate §4.1 Agenda de eventos (cola de prioridad propia con cancelación y reprogramación — esto es lo más delicado de todo el proyecto) Reloj virtual, combate, comportamiento de enemigos (guardián/errante/rastreador), efectos temporales (veneno, regeneración, trampas, cierre de puertas) §4.7 Rastro del jugador.

Uso de la respuesta: Planificar el motor de simulación, la agenda de eventos, los efectos y el rastro del jugador.

### Entrada #2

Fecha: 03–07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Auditoría inicial del proyecto.

Prompt:

> ¿Qué requisitos del enunciado y de la API cumple el proyecto y qué falta por resolver?

Uso de la respuesta: Orientar la revisión inicial del código contra el enunciado, la API y la arquitectura MVC.

### Entrada #3

Fecha: 03–07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Alcance y planificación de inventario, sistema y CLI.

Prompt:

> Dime cómo organizar el siguiente sprint de inventario, sistema y CLI, respetando el trabajo en curso del equipo.

Uso de la respuesta: Delimitar el trabajo de inventario, sistema, CLI y documentación para coordinarlo con el resto del equipo.

### Entrada #4

Fecha: 03–07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Reglas de implementación y rama de trabajo.

Prompt:

> ¿Cómo implementar mi parte con cambios simples y mínimos, trabajando en el branch eliseo y haciendo PR hacia master?

Uso de la respuesta: Organizar los cambios en la rama de trabajo y priorizar implementaciones mínimas compatibles con las restricciones.

### Entrada #5

Fecha: 03–07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Pantalla de derrota y reinicio.

Prompt:

> ¿Cómo crear una pantalla de derrota inspirada en Dark Souls, permitir otra partida y mantener los estilos en archivos .tcss?

Uso de la respuesta: Diseñar el cierre de partida y la opción de volver a jugar, separando los estilos de la vista Textual.

### Entrada #6

Fecha: 03/10/2026

Integrante: Fiorella Porras Mora.

Herramienta: Claude — Sonnet 5.5.

Objetivo: Analizar y planificar la implementación de las funcionalidades asignadas.

Prompt enviado:

> Quiero que trabajes como asistente de programación práctico y directo. Estoy desarrollando un proyecto universitario y necesito agilizar la implementación y entender lo que estoy haciendo.
>
> Mi responsabilidad es Motor de simulación y combate, incluyendo:
>
> agenda de eventos,
>
> reloj virtual,
>
> combate,
>
> comportamiento de enemigos,
>
> efectos temporales,
>
> rastro del jugador. No quiero que modifiques ni implementes funcionalidades asignadas a mis compañeros salvo que sea estrictamente necesario para integrar mi código. Antes de proponer una implementación, revisa las clases existentes y utiliza sus nombres, atributos y métodos reales. No inventes una arquitectura nueva.

Uso de la respuesta: Orientar el desarrollo de combate y efectos usando los componentes existentes y respetando la división de responsabilidades.

### Entrada #7

Fecha: 07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Escenario propio para pruebas.

Prompt:

> ¿Cómo diseñar una cripta offline llamada cripta-stormlight, inspirada en The Stormlight Archive, que también sirva para probar el juego?

Uso de la respuesta: Preparar un escenario offline adicional para ejercitar inventario, puertas, efectos, precarga y replay.

### Entrada #8

Fecha: 07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Revisión de la caché y restricciones de estructuras.

Prompt:

> ¿Qué alternativa podemos usar en Cache_Fichas para reemplazar la tabla hash y respetar las estructuras permitidas en clase?

Uso de la respuesta: Revisar la estrategia de caché y su compatibilidad con las estructuras permitidas en clase.

### Entrada #9

Fecha: 07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Ordenamientos y recorridos propios.

Prompt:

> ¿Cómo reemplazar los usos de sorted y reversed por algoritmos y recorridos propios?

Uso de la respuesta: Localizar ordenamientos y recorridos nativos que debían reemplazarse por implementaciones propias.

### Entrada #10

Fecha: 07–10/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Separación del controlador principal.

Prompt:

> ¿Cómo dividir Aplicacion.py en controladores y repartir esa separación entre los integrantes del equipo?

Uso de la respuesta: Distribuir responsabilidades entre controladores y acordar qué extracciones correspondían a cada integrante.

### Entrada #11

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Guardado binario tras el cambio de vista.

Prompt aportado:

> Mi proyecto cambió de vista a `vista/grafica` y el guardado binario quedó a medias. Quiero entender qué de lo que hicimos sigue sirviendo con esta estructura nueva.

Uso de la respuesta: Revisar qué componentes del guardado binario podían reutilizarse con la vista gráfica.

### Entrada #12

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Integración del guardado con master.

Prompt aportado:

> Al revisar el guardado contra el master actualizado, no tengo claro qué archivos siguen existiendo ni dónde encaja cada pieza.

Uso de la respuesta: Ubicar los archivos de guardado y su integración con la estructura actualizada del proyecto.

### Entrada #13

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Ubicación del archivo de partida.

Prompt aportado:

> La partida ya se guarda desde el menú, pero no sé si el archivo queda dentro del proyecto o en otro lugar.

Uso de la respuesta: Aclarar la ubicación de los archivos generados al guardar una partida desde el menú.

### Entrada #14

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Validación de guardado y carga.

Prompt aportado:

> Quiero estar segura de que guardar y cargar de verdad devuelve la partida igual, incluso con un archivo dañado o de otra versión de la cripta.

Uso de la respuesta: Revisar la restauración del estado y los casos de archivos dañados o versiones incompatibles.

### Entrada #15

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Limitaciones del guardado.

Prompt aportado:

> Para la documentación necesito tener claro qué limitaciones tiene el guardado actual, como el historial o la bitácora.

Uso de la respuesta: Identificar las limitaciones del formato de guardado para documentar qué información se conserva.

### Entrada #16

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Planificación de exploración, puertas y rastro.

Prompt aportado:

> Mi segunda asignación mezcla movimiento, puertas, rastro y guardado. Antes de programar quiero entender en qué orden conviene hacerlo y por qué.

Uso de la respuesta: Organizar la implementación de exploración y su relación con el guardado de la partida.

### Entrada #17

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Extracción de ExploracionControlador.

Prompt aportado:

> Mucho de esa lógica vive hoy dentro de `Aplicacion.py`. Me pregunto cómo separarla en un controlador sin que se rompa lo que ya funciona.

Uso de la respuesta: Revisar la extracción del movimiento, las puertas y el rastro a un controlador especializado.

### Entrada #18

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Integración de la apertura de salida con la comprobación de victoria.

Prompt aportado:

> ¿Cómo se conecta la apertura del acceso a la salida con la comprobación de victoria existente?

Uso de la respuesta: Aclarar la comunicación entre la apertura de puertas y la comprobación de victoria.

### Entrada #19

Fecha: 10/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Restricción adicional sobre tuplas.

Prompt:

> ¿Qué usos de tuplas tenemos y cómo sustituirlos respetando las restricciones del profesor?

Uso de la respuesta: Revisar las estructuras propias y distinguir sus usos de los formatos internos exigidos por bibliotecas.

### Entrada #20

Fecha: 10/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Minimapa interactivo y tamaños adaptables.

Prompt:

> ¿Cómo hacer clickeable el minimapa y adaptar los widgets a pantallas pequeñas?

Uso de la respuesta: Revisar la interacción del minimapa y la adaptación de la interfaz a pantallas pequeñas.

### Entrada #21

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Prototipo de interfaz gráfica.

Prompt:

> ¿Cómo preparar un prototipo de interfaz gráfica en un branch de pruebas, con pixel art o ASCII animado?

Uso de la respuesta: Planificar un prototipo gráfico aislado y evaluar su integración con el modelo y la API existentes.

### Entrada #22

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Arquitectura de la vista gráfica.

Prompt:

> ¿Cómo separar correctamente las responsabilidades de la vista gráfica?

Uso de la respuesta: Separar representación de la escena, recursos, entrada del usuario y coordinación de la ventana.

### Entrada #23

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Recursos gráficos y legibilidad de objetos.

Prompt:

> ¿Cómo integrar los sprites de Zerie y hacer más visibles los objetos del suelo mediante tamaño y movimiento?

Uso de la respuesta: Orientar la integración de sprites externos y la presentación visual de los objetos recogibles.

### Entrada #24

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Capacidad dinámica del inventario gráfico.

Prompt:

> ¿Cómo adaptar las casillas del inventario gráfico al valor inventario_max de cada cripta?

Uso de la respuesta: Adaptar la cuadrícula a inventario_max, usando el dato de la cripta en lugar de una cantidad fija de casillas.

### Entrada #25

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Pantalla de carga e información de red.

Prompt:

> ¿Cómo mostrar una pantalla de carga al consultar la API e indicar el presupuesto de red utilizado?

Uso de la respuesta: Revisar la carga inicial de la API y la presentación del modo de conexión y del presupuesto utilizado.

### Entrada #26

Fecha: 11/10/2026

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Regresión del método atacar.

Prompt aportado:

> Después de mover código, un test falló diciendo que `atacar` ya no existe. Quiero entender qué pudo haberse borrado de más.

Uso de la respuesta: Investigar una regresión en la interfaz del controlador tras separar responsabilidades.

### Entrada #27

Fecha: 11/10/2026

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Uso de llaves y apertura de puertas.

Prompt aportado:

> Probé el juego y no vi nada raro, pero no logré abrir una puerta con llave. No sé si la llave se usa de alguna forma especial.

Uso de la respuesta: Revisar la interacción necesaria para abrir una puerta cuando el jugador tiene su llave.

### Entrada #28

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Compatibilidad de guardados y ayudas de prueba.

Prompt:

> ¿Cómo evitar que un guardado offline se cargue contra la API y añadir un menú de cheats para probar combates difíciles?

Uso de la respuesta: Revisar la selección de la fuente de un guardado y el aislamiento de las ayudas de prueba respecto a puntajes y replay.

### Entrada #29

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Separación de servicios.

Prompt:

> ¿Qué responsabilidades podemos extraer de CriptaService para reducir su tamaño?

Uso de la respuesta: Revisar la separación de catálogo, precarga y conversión de datos para reducir responsabilidades del servicio principal.

### Entrada #30

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Configuración de audio.

Prompt:

> ¿Cómo controlar el volumen con sliders y corregir que la música se escuche demasiado baja?

Uso de la respuesta: Revisar el nivel de las pistas y diseñar controles de volumen accesibles mediante ratón y teclado.

### Entrada #31

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Eliminación de código sin uso.

Prompt:

> Dime qué módulos y submódulos no se utilizan y cuáles podemos eliminar.

Uso de la respuesta: Comprobar referencias al ensamblador antiguo y a otros módulos antes de retirarlos.

### Entrada #32

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Auditoría final de requisitos del código.

Prompt:

> ¿Qué requisitos del código quedan pendientes según el enunciado, dejando la documentación aparte?

Uso de la respuesta: Contrastar el código y las pruebas con los requisitos de red, caché, inventario, guardado, replay y rendimiento.

### Entrada #33

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Exportación del arte a PNG.

Prompt:

> ¿Cómo exportar el arte generado a tilesets PNG para evitar las tuplas utilizadas al dibujarlo durante la ejecución?

Uso de la respuesta: Evaluar la exportación de los recursos gráficos para evitar generarlos durante la ejecución del juego.

### Entrada #34

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Estrés y límites de rendimiento.

Prompt:

> ¿Qué limitaciones debemos documentar al probar el juego con 1000 enemigos y cómo relacionarlas con las restricciones del proyecto?

Uso de la respuesta: Distinguir las mediciones de la cripta de referencia de las cargas de estrés y documentar sus límites.

### Entrada #35

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Carga offline con catálogo incompatible.

Prompt:

> ¿Por qué no carga cripta-stormlight en modo offline y cómo corregirlo?

Uso de la respuesta: Investigar el conflicto entre el catálogo local de Stormlight y el catálogo persistido al jugar online.

### Entrada #36

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Recuperación del menú tras perder la conexión.

Prompt:

> ¿Cómo recuperar el menú de selección cuando se pierde Internet y la pantalla de carga queda bloqueada incluso después de reconectar?

Uso de la respuesta: Revisar la recuperación de errores de carga y el presupuesto conservado al regresar a la selección de criptas.

### Entrada #37

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Presupuesto agotado durante una partida.

Prompt:

> ¿Qué debe ocurrir cuando se agota el presupuesto de red durante una partida y cómo permitir que el usuario continúe o guarde su progreso?

Uso de la respuesta: Definir y verificar la continuidad con datos disponibles, el rechazo de acciones que requieran red y las opciones de guardar o volver al menú.


---