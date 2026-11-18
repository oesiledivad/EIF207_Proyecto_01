# Contrato: consulta de ubicación de llaves

**Spec**: [../spec.md](../spec.md) (FR-001, FR-002, FR-019 a FR-022, FR-029) | **Datos**: [../data-model.md](../data-model.md)

## Método nuevo de `CryptDataSource`

```text
@abstractmethod
key_locations(crypta_id: str) -> dict      # GET /criptas/{id}/llaves
```

Es abstracto: TODA clase que implemente `CryptDataSource` DEBE implementarlo. Esto incluye las
tres actuales y cualquier subclase falsa en `pruebas/`.

### Forma de la respuesta

```json
{"llaves": [{"id": "itm_llave_bronce", "sala": 4},
            {"id": "itm_llave_negra", "sala": 12, "enemigo": "e-1203"}]}
```

| Campo | Obligatorio | Nota |
|-------|-------------|------|
| `llaves` | Sí | Lista, posiblemente vacía |
| `llaves[].id` | Sí | Id de la llave (el mismo que `llave` en las salidas cerradas) |
| `llaves[].sala` | Sí | Entero; sala donde la llave queda disponible |
| `llaves[].enemigo` | No | Id de la instancia que la suelta; la llave está disponible en `sala`, donde ese enemigo inicia |

Una llave puede repetirse con distintas salas (varias ubicaciones). El orden de la lista NO tiene
significado; el modelo no depende de él (principio II).

### Implementaciones

| Clase | Comportamiento |
|-------|----------------|
| `NetworkAdapter` | `_request(f"/criptas/{id}/llaves")`. Cuenta en `requests_made`, respeta `presupuesto_solicitudes`, reintentos 429 incluidos. Errores: `PresupuestoAgotado`, `RuntimeError` |
| `AdaptadorOffline` | 1) `almacen.leer_llaves(id)` si la cripta está en la caché; 2) archivo `cripta_<id>_llaves.json` del paquete. Si no hay ninguno: `FileNotFoundError`. NO cuenta solicitudes (`requests_made` es 0). Una cripta que está en la caché se juega SOLO con la caché (no se mezclan versiones) |
| `Guardar_Llamadas_API` | `key_locations(crypta_id, datos)`: graba `cripta_<id>_llaves.json` con `guardar_llamada`, igual que las demás consultas del grabador. El paquete `datos_offline` puede incluir ese archivo cuando el curso lo publique |

`_FuenteSincronizada` envuelve cualquier método por `__getattr__`, por lo que la consulta queda
protegida frente a la precarga en segundo plano sin cambios.

## Persistencia en `AlmacenDisco`

| Método | Efecto |
|--------|--------|
| `leer_llaves(cripta_id) -> dict o None` | Lee `criptas/<id>/llaves.json`; archivo ausente o dañado equivale a `None` |
| `guardar_llaves(cripta_id, datos)` | Escritura atómica (`_escribir_json`) en la misma ruta |

La ruta está dentro de `criptas/<id>/`, la carpeta que `validar_cripta(id, version)` borra y
recrea si la versión cambió. Por eso:

- Misma versión: la segunda verificación lee el archivo y NO solicita red (FR-020, SC-005).
- Versión distinta: el archivo desaparece y se consulta de nuevo (FR-021).
- Se guarda solo después de una respuesta válida de la fuente y solo si la cripta está en disco
  (`_cripta_en_disco`), igual que el esqueleto.

## Método nuevo de `CriptaService`

```text
obtener_ubicaciones_llaves(cripta_id: str) -> list[UbicacionLlave]
validar_cripta_en_disco(detalles: DetallesCripta) -> bool       # sin consultar el catálogo
```

`obtener_ubicaciones_llaves`:

1. Si `_cripta_en_disco`, lee `leer_llaves`; si hay datos válidos, los parsea y los devuelve sin
   tocar la fuente.
2. Si no, llama `key_locations` de la fuente, guarda el resultado en disco si corresponde y
   parsea con `parsear_llaves`.
3. Cualquier falla de obtención (`PresupuestoAgotado`, `RuntimeError`, `OSError`, `ValueError`,
   `FileNotFoundError`, `NotImplementedError`) se convierte en `UbicacionLlavesNoDisponible`.
   No se emite veredicto (FR-022).
4. Una respuesta presente pero malformada (sin `llaves`, o con entradas sin `id` o `sala` enteros)
   se trata como no disponible, no como "sin llaves". Una lista `llaves` vacía y válida es un
   dato legítimo (cripta sin llaves).

`validar_cripta_en_disco` envuelve `AlmacenDisco.validar_cripta` y fija `_cripta_en_disco`, sin la
solicitud de versión de catálogo que hoy hace `preparar_persistencia`. `--verificar` lo usa; la
partida normal sigue usando `preparar_persistencia`.

## Conversión a DTO

`FactoryDto_Partida.parsear_llaves(respuesta) -> list[UbicacionLlave]`: usa `dict` solo para leer el
JSON (permitido por la constitución). Convierte `sala` con `int`, `enemigo` a `str` o `None`,
descarta entradas sin `id` y levanta `ValueError` en la estructura general inválida.

## Contrato del modelo (sin E/S)

```text
verificar(sala_inicial: int, sala_salida: int, llave_salida: str,
          salas: list[SalaModelo], ubicaciones: list[UbicacionLlave]) -> ResultadoVerificacion
```

- NO conoce HTTP, archivos ni vista; recibe solo DTO ya parseados.
- NO modifica `salas` ni `ubicaciones`.
- Es determinista: mismas entradas, mismo resultado, sin importar el orden de las listas de
  entrada.
- NO contiene datos de una cripta (FR-029).
- No lanza por falta de llaves: devuelve `no_verificable` solo por datos inválidos del esqueleto
  (la falta de ubicaciones la decide quien llama, antes de invocar).
