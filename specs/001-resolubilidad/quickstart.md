# Quickstart: validar la verificación de resolubilidad

**Spec**: [spec.md](spec.md) | **Contratos**: [contracts/](contracts/) | **Modelo**: [data-model.md](data-model.md)

Guía para comprobar de punta a punta que la capacidad funciona, una vez implementada. No contiene
código de implementación. Comandos para Windows con CMD, desde la raíz del repositorio.

## Requisitos previos

1. Python 3.13 y uv instalados; `uv sync` ejecutado.
2. Rama `kyara` con la spec y este plan confirmados.
3. Para las pruebas con red: acceso al servicio. Para las pruebas sin red: una caché
   (`--cache-dir`) descargada antes o un paquete que incluya `cripta_<id>_llaves.json`.

El paquete `datos_offline` actual NO trae llaves: con él, `--verificar --offline` debe terminar con
código 2 y el aviso "resolubilidad no verificada" (escenario 6).

## Escenarios

### 1. Pruebas automatizadas (SC-001, SC-002)

```text
uv run python -m unittest discover -s pruebas -p "test_resolubilidad.py"
uv run python -m unittest discover -s pruebas -p "test_indice_llaves.py"
uv run python -m unittest discover -s pruebas -p "test_llaves_adaptadores.py"
uv run python -m unittest discover -s pruebas -p "test_verificar_cli.py"
uv run python -m unittest discover -s pruebas -p "test_inicio_verificacion.py"
uv run python -m unittest discover -s pruebas -p "test_bench_resolubilidad.py"
```

Resultado esperado: todas en verde. Cubren, con criptas armadas en la propia prueba (sin datos de
cripta reales en el código):

- Resoluble con una sola llave; con llaves encadenadas; con una llave obtenible innecesaria; orden
  idéntico en dos ejecuciones; llave de enemigo errante ubicada en su sala de inicio.
- Ciclo de `llave_salida` consigo misma; ciclo de dos llaves con puertas y salas; reporte con
  llaves, frontera y ubicaciones; ciclo idéntico en dos ejecuciones; varios ciclos, cada uno
  desde su menor id y en orden.
- Bordes: llave en la sala inicial, llave inalcanzable con puerta existente, llave obtenible sin
  puerta que llegue a la sala de salida, varias puertas con la misma llave, llave con varias
  ubicaciones, llave sin ubicación, salidas dirigidas con la puerta declarada en un solo lado.

Los ids de llave y de sala de los escenarios los define cada prueba para ese caso; los reales solo
aparecen si la prueba lee un paquete.

### 2. Resultado en consola, cripta resoluble (FR-017, SC-006)

```text
uv run python -m cripta --verificar <cripta> --offline --cache-dir <carpeta_con_llaves>
echo %ERRORLEVEL%
```

Esperado: primera línea `Cripta <cripta> (version <v>): RESOLUBLE`, lista numerada con todas las
llaves obtenibles, `Solicitudes de red: 0/<presupuesto>`, código `0`, y ninguna ventana.

### 3. Cripta no resoluble en consola (FR-009 a FR-013)

Usar una caché o paquete cuya cripta tenga `llave_salida` detrás de la única puerta que ella
abre (o preparar uno con la prueba del punto 1).

```text
uv run python -m cripta --verificar <cripta_bloqueada> --offline --cache-dir <carpeta>
echo %ERRORLEVEL%
```

Esperado: `NO RESOLUBLE`, sección de llaves inobtenibles con su sala (y enemigo si aplica), al
menos una puerta de la frontera con su llave, la sección de ciclos con `Ciclo 1: <llave> -> <llave>`
y las puertas testigo, código `1`. Repetir el comando: la salida debe ser idéntica byte a byte
(SC-002).

### 4. Partida bloqueada y `--forzar` (FR-015, FR-016, SC-007)

```text
uv run python -m cripta --cripta <cripta_bloqueada> --offline --cache-dir <carpeta>
uv run python -m cripta --cripta <cripta_bloqueada> --offline --cache-dir <carpeta> --forzar
```

Esperado: en el primer comando, al elegir la cripta e iniciar, la partida NO inicia y la pantalla
muestra el reporte con al menos una puerta bloqueada y su llave. En el segundo, la partida inicia
y el reporte queda en la bitácora.

### 5. Reutilización de la ubicación de llaves (FR-019 a FR-021, SC-005)

Con red:

```text
uv run python -m cripta --verificar <cripta> --cache-dir <carpeta>
uv run python -m cripta --verificar <cripta> --cache-dir <carpeta>
```

Esperado: la línea `Solicitudes de red` de la primera ejecución incluye la consulta de llaves; la
segunda NO la repite y muestra menos solicitudes (no se vuelve a pedir datos guardados con la misma
versión). Si cambia la versión de la cripta, la segunda ejecución vuelve a consultar.

### 6. Ubicación de llaves no disponible (FR-022)

```text
uv run python -m cripta --verificar cripta-01 --offline
echo %ERRORLEVEL%
```

Esperado con el paquete actual: `resolubilidad no verificada`, código `2`, sin la palabra
RESOLUBLE ni NO RESOLUBLE. En una partida normal sin llaves disponibles, la partida inicia con el
aviso "resolubilidad no verificada", con y sin `--forzar`.

### 7. Medición (FR-023, FR-024, FR-026, SC-003, SC-004)

```text
uv run python -m cripta --bench --semilla 42
uv run python -m cripta --bench --semilla 42
```

Esperado en la sección "Resolubilidad": la verificación contra la alternativa ingenua por tamaño
(la ingenua pierde y la brecha crece), el escalado por 10 de tamaño (menos de 15 veces), el
tiempo de la referencia si el paquete trae llaves (menos de 200 ms) o el mensaje de que no las
trae, el tiempo de la cripta sintética de al menos 10 veces el esqueleto más grande del paquete
(menos de 200 ms, M7), la comparación de índices y el costo del reporte. Con la misma semilla, los conteos
(salas, salidas, llaves, llaves en el orden) coinciden entre ejecuciones; los tiempos pueden
variar. `--bench` no abre ventana.

## Criterios de aceptación de la guía

| Criterio | Cómo se comprueba | FR / SC |
|----------|-------------------|---------|
| Veredicto y orden correctos | Escenarios 1 y 2 | FR-006, FR-007, SC-001 |
| Reporte y ciclos deterministas | Escenarios 1 y 3 | FR-009 a FR-013, SC-002 |
| Códigos 0, 1 y 2 | Escenarios 2, 3 y 6 | FR-018a |
| Bloqueo y `--forzar` | Escenario 4 | FR-015, FR-016, SC-007 |
| Sin vista en `--verificar` y `--bench` | Escenarios 2, 3 y 7 | FR-017, FR-028, SC-006 |
| Reutilización y presupuesto | Escenario 5 | FR-019 a FR-021, SC-005 |
| Rendimiento con evidencia | Escenario 7 | FR-023, FR-024, FR-026, SC-003, SC-004 |

## Resultado de la validación

Ejecutada en la rama `kyara` (T085). Los paquetes de los escenarios 2, 3 y 4 son copias de `datos_offline` hechas fuera del repositorio, con un `cripta_cripta-01_llaves.json` armado para cada caso; `datos_offline` no se modificó. No se ejecutó la suite completa ni T086.

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| 1. Pruebas automatizadas | CUMPLE | Las seis pruebas, una por módulo (`python -m unittest pruebas.<módulo>`): `test_resolubilidad` 30, `test_indice_llaves` 6, `test_llaves_adaptadores` 8, `test_verificar_cli` 6, `test_inicio_verificacion` 6 y `test_bench_resolubilidad` 6, todas en verde |
| 2. Consola, cripta resoluble | CUMPLE | `RESOLUBLE`, 2 llaves en orden (bronce en la sala 3, negra en la sala 5 con su enemigo), `Solicitudes de red: 0/9`, código 0, sin ventana |
| 3. Consola, cripta no resoluble | CUMPLE | `NO RESOLUBLE`, llave inobtenible con su sala y causa «en ciclo», una puerta de la frontera, `Ciclo 1: itm_llave_negra -> itm_llave_negra` con su puerta testigo, código 1; la segunda ejecución es idéntica byte a byte (`cmp`) |
| 4. Partida bloqueada y `--forzar` | CUMPLE sin ventana | Se ejecutó `Aplicacion.iniciar_partida` con la cripta bloqueada: sin `--forzar` da `ok=False`, `activa=False` y el reporte completo como motivo; con `--forzar` da `ok=True`, `activa=True`; con la cripta resoluble inicia. No se abrió la ventana gráfica: la parte visual del reporte en pantalla queda para una comprobación manual |
| 5. Reutilización con red | CUMPLE | Con `cripta-02` del servicio y una caché nueva: primera ejecución `Solicitudes de red: 3/23` (incluye la consulta de llaves), segunda `1/23`, y quedó `criptas/cripta-02/llaves.json`. `cripta-01` no existe en el servicio (error 404), por eso se usó `cripta-02`. El cambio de versión lo cubren las pruebas de `test_llaves_adaptadores` |
| 6. Ubicación no disponible | CUMPLE | `--verificar cripta-01 --offline` con el paquete actual: `resolubilidad no verificada`, código 2, sin las palabras RESOLUBLE ni NO RESOLUBLE |
| 7. Medición | CUMPLE | `--bench --semilla 42` dos veces: conteos idénticos con los tiempos enmascarados, sin ventana ni `arcade`, M1 a M7 impresos; salida en `mediciones.txt`. M3 imprime «sin llaves en el paquete» porque el paquete no trae llaves |
