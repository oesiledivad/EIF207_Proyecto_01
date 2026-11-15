# Contrato: línea de comandos y salida de la verificación

**Spec**: [../spec.md](../spec.md) (FR-014 a FR-018a, FR-026, FR-028) | **Datos**: [../data-model.md](../data-model.md)

## Banderas

| Bandera | Efecto |
|---------|--------|
| `--verificar CRIPTA` | Ejecuta solo la verificación de la cripta e imprime el resultado. NO abre la vista. Exclusiva con `--replay`, `--bench` y `--grafica` (mismo grupo de `bootstrap`) |
| `--forzar` | Permite iniciar una partida aunque la cripta no sea resoluble. Solo afecta la partida interactiva; con `--verificar`, `--bench` o `--replay` se ignora |
| `--offline` | Con `--verificar`: usa solo caché y paquete, sin solicitudes de red |
| `--cache-dir`, `--offline-dir` | Igual que hoy; con `--verificar` determinan dónde se lee y se guarda la ubicación de llaves |
| `--semilla N` | Con `--bench`: semilla de las criptas sintéticas. Vacía equivale a 42. Sin efecto en `--verificar` |
| `--bench` | Incluye la sección "Resolubilidad" (mediciones M1 a M6 del plan) |

`--verificar` sin id de cripta, o con una bandera exclusiva, termina con el error de uso de
`argparse` (código 2).

## Códigos de salida de `--verificar` (FR-018a)

| Código | Significado | Cuándo |
|--------|-------------|--------|
| 0 | Resoluble | Veredicto positivo |
| 1 | No resoluble | Veredicto negativo, con reporte |
| 2 | Sin veredicto | Ubicación de llaves no disponible, datos inválidos, cripta inexistente, presupuesto agotado antes de obtener los datos, o error de uso |

El código 0 NO DEBE devolverse nunca sin veredicto positivo, ni con una cripta no resoluble.

## Salida estándar

Texto en español, una cosa por línea, sin colores ni adornos, estable entre ejecuciones
(determinista). Los ids se imprimen tal como llegan del servicio. La primera línea siempre es el
veredicto, para que las pruebas y los usuarios lean `linea[0]`.

### Resoluble (código 0)

```text
Cripta <cripta_id> (version <version>): RESOLUBLE
Orden de obtencion de llaves (<n> llaves):
  1. <llave> en sala <sala>
  2. <llave> en sala <sala> (suelta el enemigo <enemigo>)
  ...
Solicitudes de red: <usadas>/<presupuesto>
```

`<n>` puede ser 1 (solo `llave_salida`). Las llaves van en el orden de obtención (ronda, id de
sala, id de llave). Lista TODAS las obtenibles, incluidas las no necesarias para ganar.

### No resoluble (código 1)

```text
Cripta <cripta_id> (version <version>): NO RESOLUBLE
Motivo: <llave de salida no obtenible | ninguna puerta con la llave de salida llega a la sala de salida>
Llaves que no pueden obtenerse (<n>):
  - <llave>: sala <sala> [(enemigo <enemigo>)] ; <causa>
  - <llave>: ubicaciones: sala <s1>, sala <s2> (enemigo <enemigo>) ; <causa>
  - <llave>: sin ubicacion publicada
Puertas bloqueadas en la frontera (<n>):
  - sala <origen> salida <direccion> hacia sala <destino> exige <llave>
Ciclos de dependencia (<n>):
  Ciclo 1: <llave A> -> <llave B> -> <llave A>
    <llave A> esta en sala <s> detras de la puerta sala <o> salida <d> hacia sala <t> que exige <llave B>
    <llave B> esta en sala <s> detras de la puerta sala <o> salida <d> hacia sala <t> que exige <llave A>
Solicitudes de red: <usadas>/<presupuesto>
```

Reglas:

- Las llaves se ordenan por id. Las ubicaciones de una llave, por id de sala. Las puertas, por
  (id de llave, orden de inserción). Los ciclos, por el id de su llave de menor id.
- Cada ciclo se imprime empezando en su llave de menor id y en el sentido "esta detrás de una
  puerta que exige la siguiente". El último nombre repite el primero.
- Un ciclo de una sola llave se imprime `Ciclo 1: <llave> -> <llave>`.
- Si no hay ciclos, la sección se imprime con `(0)` y sin entradas; la causa de cada llave dice
  entonces `sin ubicacion`, `sala desconectada` o `depende de <llave>`.
- Una llave con varias ubicaciones y ninguna alcanzable las lista todas (FR-011).

### Sin veredicto (código 2)

```text
Cripta <cripta_id>: resolubilidad no verificada
Motivo: <ubicacion de llaves no disponible | datos invalidos: <detalle>>
```

Las advertencias de datos (ubicaciones descartadas, salidas a salas inexistentes) van a la salida de
errores, no a la estándar, con el prefijo `Aviso:`.

## Presupuesto y red

- Con `--verificar` sin `--offline` se pide, en orden: datos de la cripta, páginas del esqueleto y
  la ubicación de llaves. Cada una cuenta en el presupuesto (principio V). Lo ya guardado con la
  misma versión no se pide de nuevo.
- Con `--offline`, `requests_made` es 0 y `Solicitudes de red` imprime `0/<presupuesto>`.
- Nunca se importa `arcade` ni se instancia la vista (principio III, FR-028).

## Partida interactiva

Contrato visible de `Aplicacion.iniciar_partida` (extiende `ResultadoInicio`):

| Situación | `ok` | `motivo` / `aviso` |
|-----------|------|---------------------|
| Resoluble | `True` | `aviso` con el veredicto y el orden de llaves; también en la bitácora |
| No resoluble, sin `--forzar` | `False` | `motivo` con el mismo reporte que `--verificar` (código 1) |
| No resoluble, con `--forzar` | `True` | `aviso` con el veredicto negativo; reporte en la bitácora |
| Sin veredicto | `True` | `aviso` = `resolubilidad no verificada`, sin la palabra resoluble ni no resoluble, con o sin `--forzar` |

Con `ok=False` por bloqueo, `EstadoPartida.activa` es `False` y NO se crea registro de partida.
`--replay` y la carga de partidas guardadas inician con `verificar=False`.

## Salida de `--bench` (sección "Resolubilidad")

Una línea por medición, mismo estilo de `bench.py`: nombre, parámetros (tamaño, semilla),
tiempo total y por operación. Dos ejecuciones con la misma semilla generan criptas idénticas y
reportan los mismos conteos (S, E, K, llaves en el orden); los tiempos varían por la máquina.
