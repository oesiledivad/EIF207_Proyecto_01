# Contrato: interfaz serializable del conocimiento (para la spec 004)

**Spec**: [../spec.md](../spec.md) (FR-015, FR-017) | **Decisión**: D13 en [../research.md](../research.md)

Esta capacidad NO define el formato binario del guardado ni la línea de tiempo: eso es de la spec
004. Aquí se fija únicamente la forma en que el modelo entrega y recibe el conocimiento, con
estructuras simples (listas de enteros pequeños) que cualquier formato puede escribir.

## Instantánea

`ConocimientoJugador.instantanea()` devuelve una lista de enteros:

| Posición | Contenido |
|----------|-----------|
| 0 | Versión del formato de la instantánea (hoy 1) |
| 1 | `n`: cantidad de ids de sala (`max_id + 1`) |
| 2 a `n + 1` | Estado de cada sala por id: 0, 1 o 2 |
| `n + 2` a `5n + 1` | Memoria de cada salida por clave (`sala * 4 + dirección`): 0, 1 o 2 |

Reglas:

- Todos los valores caben en un byte sin signo.
- El largo siempre es `1 + 1 + n + 4n = 5n + 2`.
- La instantánea NO contiene las salidas entrantes, los nombres ni el costo: se derivan del esqueleto
  de la misma versión de cripta.
- Dos conocimientos iguales producen instantáneas idénticas (SC-005).

## Restauración

`ConocimientoJugador.restaurar(instantanea)`:

- Falla con error de valor si la versión del formato no es 1, si `n` no coincide con el esqueleto
  ensamblado, si el largo es incorrecto o si algún valor está fuera de 0 a 2.
- Reemplaza las dos listas completas y vacía el registro. No toca el historial: la restauración
  ocurre al cargar, con el historial limpio.
- Tras restaurar, el mapa conocido es idéntico al del momento de guardar (historia 6, escenario 3).

## Registro cronológico

`ConocimientoJugador.registro` es una lista de cambios `[tiempo, tipo, indice, valor]`:

| Campo | Significado |
|-------|-------------|
| `tiempo` | Reloj virtual al registrar el cambio |
| `tipo` | 0 estado de sala, 1 memoria de puerta |
| `indice` | Id de sala (tipo 0) o clave de salida (tipo 1) |
| `valor` | Valor nuevo, 0 a 2 |

Reglas:

- Solo se anexan cambios reales (valor distinto del actual).
- El orden es el de ocurrencia. Un retroceso recorta el final de la lista.
- `longitud_registro()` devuelve cuántos cambios hay; la línea de tiempo puede guardar ese número en
  cada instante que le interese.

## Reconstrucción de un instante pasado

`ConocimientoJugador.reconstruir(instantanea_base, registro, n)` devuelve un conocimiento nuevo con
el estado tras aplicar los primeros `n` cambios del `registro` sobre la `instantanea_base`:

- `instantanea_base` es la instantánea del instante 0 (la que deja `iniciar`), que la spec 004
  conserva junto al registro.
- `0 <= n <= len(registro)`; fuera de ese rango, error de valor.
- Cuesta O(S + n). No modifica el conocimiento vivo ni el historial.
- El resultado se puede exportar con `instantanea()` o convertir en `MapaConocido`.

Variante por tiempo: `reconstruir_hasta_tiempo(instantanea_base, registro, t)` aplica los cambios
con `tiempo <= t`. Es exacta solo en instantes que son frontera de acción; la forma por prefijo es la
canónica.

## Lo que NO es parte del contrato

- Cómo se escribe en disco, el orden de secciones del archivo binario o su compresión.
- El estado del viaje: no se guarda (D14).
- Los pesos, nombres y contenido de salas: vienen del esqueleto y del servicio.

## Puntos a confirmar con la spec 004

- C12: si la línea de tiempo prefiere identificar un instante por prefijo del registro (propuesto) o
  por tiempo.
- Si el guardado debe incluir la instantánea base del instante 0 o puede recomputarla desde el
  esqueleto y la sala inicial (es determinista: se propone recomputarla).
