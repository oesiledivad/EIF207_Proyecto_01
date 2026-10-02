# Cripta API

API de solo lectura para consultar definiciones reutilizables de mazmorras ("criptas").

- **Versión:** 1.0.0
- **Especificación:** OpenAPI 3.1.0

## Autenticación / Headers

Casi todos los endpoints requieren el header:

| Header               | Tipo            | Descripción                                                                 |
|----------------------|-----------------|-----------------------------------------------------------------------------|
| `X-Cripta-Client-Id` | `string` (UUID) | Identificador estable por cliente, usado solo para el conteo de rate-limit. |

## Manejo de errores

Todos los endpoints pueden devolver estas respuestas de error:

| Código | Significado                   | Cuerpo                |
|--------|-------------------------------|-----------------------|
| `400`  | Solicitud malformada          | `ErrorResponse`       |
| `404`  | El recurso no existe          | `ErrorResponse`       |
| `429`  | Límite de frecuencia excedido | `RateLimitedResponse` |
| `500`  | Contenido publicado inválido  | `ErrorResponse`       |

```json
// ErrorResponse
{ "error": "string" }

// RateLimitedResponse
{ "error": "string", "reintentar_en": 1 }
```

---

## Endpoints

### `GET /v1/criptas`
Lista las definiciones de mazmorras publicadas.

**Headers:** `X-Cripta-Client-Id` (requerido)

**Respuesta 200 — `CriptasResponse`:**
```json
{
  "criptas": [
    { "id": "string", "nombre": "string", "salas": 0, "dificultad": 0 }
  ]
}
```

---

### `GET /v1/criptas/{dungeon_id}`
Datos generales de una mazmorra.

**Parámetros:**
| Nombre | En | Requerido | Tipo |
|-------------|---|---|---|
| `dungeon_id` | path | sí | `string` |
| `X-Cripta-Client-Id` | header | sí | `string` (UUID) |
-----------------------------------
**Respuesta 200 — `DungeonGeneral`:**
```json
{
  "id": "string",
  "version": "string",
  "salas_total": 0,
  "paginas": 0,
  "salas_por_pagina": 0,
  "sala_inicial": 0,
  "sala_salida": 0,
  "llave_salida": "string",
  "presupuesto_solicitudes": 0,
  "inventario_max": 0,
  "jugador": {
    "vida_max": 1,
    "ataque": 0,
    "defensa": 0,
    "velocidad": 1
  }
}
```

---

### `GET /v1/criptas/{dungeon_id}/version`
Chequeo liviano de la versión de una mazmorra (útil para invalidar caché sin traer todo el contenido).

**Parámetros:**
| Nombre | En | Requerido | Tipo |
|---|---|---|---|
| `dungeon_id` | path | sí | `string` |
| `X-Cripta-Client-Id` | header | sí | `string` (UUID) |

**Respuesta 200 — `DungeonVersion`:**
```json
{ "id": "string", "version": "string" }
```

---

### `GET /v1/criptas/{dungeon_id}/salas`
Devuelve una página del esqueleto de salas (habitaciones y sus salidas), paginado.

**Parámetros:**
| Nombre | En | Requerido | Tipo | Descripción |
|---|---|---|---|---|
| `dungeon_id` | path | sí | `string` | |
| `X-Cripta-Client-Id` | header | sí | `string` (UUID) | |
| `pagina` | query | sí | `integer` (≥1) | Número de página (base 1); máximo 50 salas por página. |

**Respuesta 200 — `SkeletonPage`:**
```json
{
  "pagina": 1,
  "total_paginas": 3,
  "salas": [
    {
      "id": 1,
      "nombre": "string",
      "salidas": {
        "N": { "sala": 2, "cerrada": false, "llave": null, "cierre_automatico": null }
      }
    }
  ]
}
```
> Las claves válidas de `salidas` son `N`, `S`, `E`, `O`.

---

### `GET /v1/criptas/{dungeon_id}/contenido`
Devuelve el contenido colocado (enemigos, objetos, trampas) para hasta 10 salas.

**Parámetros:**
| Nombre | En | Requerido | Tipo | Descripción |
|---|---|---|---|---|
| `dungeon_id` | path | sí | `string` | |
| `X-Cripta-Client-Id` | header | sí | `string` (UUID) | |
| `salas` | query | sí | `string` | Lista separada por comas de 1 a 10 ids de sala distintos. |

**Respuesta 200 — `ContenidoResponse`:**
```json
{
  "contenido": [
    {
      "sala": 1,
      "enemigos": [
        { "instancia": "string", "tipo": "string", "vida": 10 }
      ],
      "objetos": ["string"],
      "trampas": [
        { "instancia": "string", "tipo": "string" }
      ]
    }
  ]
}
```

---

### `GET /v1/catalogo/version`
Chequeo liviano de la versión global del catálogo.

**Headers:** `X-Cripta-Client-Id` (requerido)

**Respuesta 200 — `CatalogVersion`:**
```json
{ "version": "string" }
```

---

### `GET /v1/catalogo`
Devuelve entradas del catálogo para hasta 10 ids.

**Parámetros:**
| Nombre | En | Requerido | Tipo | Descripción |
|---|---|---|---|---|
| `X-Cripta-Client-Id` | header | sí | `string` (UUID) | |
| `ids` | query | sí | `string` | Lista separada por comas de 1 a 10 ids de catálogo distintos. |

**Respuesta 200 — `CatalogoResponse`:**
```json
{
  "entidades": [
    { "clase": "enemigo", "...": "ver tabla de modelos abajo" }
  ]
}
```
> Cada elemento de `entidades` es uno de los tipos descritos en [Entidades del catálogo](#entidades-del-catálogo), discriminado por el campo `clase`.

---

### `GET /v1/catalogo/{catalog_id}`
Devuelve una sola entrada del catálogo (sin envolver en un objeto contenedor).

**Parámetros:**
| Nombre | En | Requerido | Tipo |
|---|---|---|---|
| `catalog_id` | path | sí | `string` |
| `X-Cripta-Client-Id` | header | sí | `string` (UUID) |

**Respuesta 200:** una de las entidades del catálogo (ver abajo), según el valor de `clase`.

---

## Entidades del catálogo

Todas las entidades comparten un discriminador `clase`. El valor de `clase` determina el esquema:

| `clase`               | Esquema        |
|-----------------------|----------------|
| `Enemigo.py`             | `Enemy`        |
| `arma`                | `Weapon`       |
| `armadura`            | `Armor`        |
| `pocion`              | `Potion`       |
| `antidoto`            | `Antidote`     |
| `llave`               | `Key`          |
| `antorcha`            | `Torch`        |
| `pergamino_retroceso` | `RewindScroll` |
| `trampa`              | `Trap`         |

### `Enemy`
| Campo            | Tipo               | Notas                                       |
|------------------|--------------------|---------------------------------------------|
| `id`             | `string`           |                                             |
| `nombre`         | `string`           |                                             |
| `clase`          | `"enemigo"`        |                                             |
| `vida_max`       | `integer`          | > 0                                         |
| `ataque`         | `integer`          |                                             |
| `defensa`        | `integer`          |                                             |
| `velocidad`      | `integer`          | > 0                                         |
| `comportamiento` | `string`           | uno de: `guardián`, `errante`, `rastreador` |
| `suelta`         | `string[] \| null` | ids de objetos que suelta al morir          |

### `Weapon`
| Campo          | Tipo      |
|----------------|-----------|
| `id`           | `string`  |
| `nombre`       | `string`  |
| `clase`        | `"arma"`  |
| `peso`         | `integer` |
| `valor`        | `integer` |
| `ataque_bonus` | `integer` |

### `Armor`
| Campo           | Tipo         |
|-----------------|--------------|
| `id`            | `string`     |
| `nombre`        | `string`     |
| `clase`         | `"armadura"` |
| `peso`          | `integer`    |
| `valor`         | `integer`    |
| `defensa_bonus` | `integer`    |

### `Potion`
| Campo                   | Tipo              | Notas |
|-------------------------|-------------------|-------|
| `id`                    | `string`          |       |
| `nombre`                | `string`          |       |
| `clase`                 | `"pocion"`        |       |
| `peso`                  | `integer`         |       |
| `valor`                 | `integer`         |       |
| `cura`                  | `integer \| null` |       |
| `modificador_velocidad` | `integer \| null` |       |
| `duracion`              | `integer \| null` |       |

### `Antidote`
| Campo    | Tipo         |
|----------|--------------|
| `id`     | `string`     |
| `nombre` | `string`     |
| `clase`  | `"antidoto"` |
| `peso`   | `integer`    |
| `valor`  | `integer`    |

### `Key`
| Campo    | Tipo                        | Notas                        |
|----------|-----------------------------|------------------------------|
| `id`     | `string`                    |                              |
| `nombre` | `string`                    |                              |
| `clase`  | `"llave"`                   |                              |
| `peso`   | `integer`                   |                              |
| `valor`  | `integer`                   |                              |
| `abre`   | `string \| integer \| null` | id o número de sala que abre |

### `Torch`
| Campo      | Tipo         |
|------------|--------------|
| `id`       | `string`     |
| `nombre`   | `string`     |
| `clase`    | `"antorcha"` |
| `peso`     | `integer`    |
| `valor`    | `integer`    |
| `duracion` | `integer`    |

### `RewindScroll`
| Campo    | Tipo                    |
|----------|-------------------------|
| `id`     | `string`                |
| `nombre` | `string`                |
| `clase`  | `"pergamino_retroceso"` |
| `peso`   | `integer`               |
| `valor`  | `integer`               |

### `Trap` (catálogo)
| Campo    | Tipo              | Notas                       |
|----------|-------------------|-----------------------------|
| `id`     | `string`          |                             |
| `nombre` | `string`          |                             |
| `clase`  | `"trampa"`        |                             |
| `daño`   | `integer`         |                             |
| `rearme` | `integer \| null` | tiempo de rearme, si aplica |

---

## Otros modelos

### `DungeonSummary`
Usado en la lista de `/v1/criptas`.
| Campo | Tipo |
|---|---|
| `id` | `string` |
| `nombre` | `string` |
| `salas` | `integer` |
| `dificultad` | `integer` |

### `PlayerInitial`
Estadísticas iniciales del jugador, incluidas en `DungeonGeneral`.
| Campo | Tipo | Notas |
|---|---|---|
| `vida_max` | `integer` | > 0 |
| `ataque` | `integer` | |
| `defensa` | `integer` | |
| `velocidad` | `integer` | > 0 |

### `Sala.py`
Habitación dentro del esqueleto (`SkeletonPage`).
| Campo | Tipo |
|---|---|
| `id` | `integer` |
| `nombre` | `string` |
| `salidas` | mapa de `N`/`S`/`E`/`O` → `Exit` |

### `Exit`
Una salida dirigida desde una sala (estado de definición inicial, no estado en vivo).
| Campo | Tipo | Notas |
|---|---|---|
| `sala` | `integer` | sala destino |
| `cerrada` | `boolean \| null` | |
| `llave` | `string \| null` | id de la llave que la abre |
| `cierre_automatico` | `integer \| null` | > 0; tiempo hasta cierre automático |

### `EnemyPlacement`
Instancia de un enemigo colocado en una sala (`RoomContentEntry.enemigos`).
| Campo | Tipo |
|---|---|
| `instancia` | `string` |
| `tipo` | `string` (id de catálogo) |
| `vida` | `integer \| null` |

### `TrapPlacement`
Instancia de una trampa colocada en una sala (`RoomContentEntry.trampas`).
| Campo | Tipo |
|---|----|
| `instancia` | `string` |
| `tipo` | `string` (id de catálogo) |

### `RoomContentEntry`
| Campo      | Tipo                         |
|------------|------------------------------|
| `sala`     | `integer`                    |
| `enemigos` | `EnemyPlacement[]`           |
| `objetos`  | `string[]` (ids de catálogo) |
| `trampas`  | `TrapPlacement[]`            |