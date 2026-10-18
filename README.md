# Cripta

Proyecto de Estructuras de Datos II — II Ciclo 2026.

Juego de mazmorra dirigido por eventos.

## Requisitos

- Python 3.13 o superior (lo exige `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/) como gestor de entorno y dependencias
- Dependencias (las instala `uv sync`): `requests` y `arcade` (vista gráfica)

## Instalación

### 1. Instalar uv

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verificar que quedó instalado:
```bash
uv --version
```

### 2. Clonar el repositorio e instalar dependencias

```bash
git clone https://github.com/oesiledivad/EIF207_Proyecto_01.git
cd EIF207_Proyecto_01
uv sync
```

`uv sync` crea el entorno virtual automáticamente y instala las dependencias
declaradas en `pyproject.toml` según lo fijado en `uv.lock`.

## Ejecución

El juego se juega en una ventana hecha con Arcade.

```bash
uv run cripta                    # en red (usa la caché persistente)
uv run cripta --offline          # sin red: lo ya descargado + paquete del curso
uv run cripta --cache-size 25    # tope de fichas en memoria (§4.4, por defecto 25)
uv run cripta --replay partidas/<archivo>.log   # reproduce una partida sin ventana
uv run cripta --bench            # mediciones por subsistema, sin red ni ventana
```

Otras banderas: `--cache-dir` (carpeta de la caché, por defecto `.cripta_cache`),
`--offline-dir` (paquete de respuestas del curso, por defecto `datos_prueba`),
`--log-dir` (carpeta de registros, por defecto `partidas`), `--puntajes`,
`--cripta`, `--nombre` y `--semilla`.

### Modo `--offline`

Lee las respuestas desde disco con el mismo contrato que el cliente de red:

1. Primero la caché persistente (`--cache-dir`): lo que se fue descargando al
   jugar en línea (lista de criptas, datos generales, esqueleto, contenido de
   las salas visitadas o precargadas y fichas del catálogo).
2. Solo lo que no esté en la caché se toma del paquete del curso (`--offline-dir`).

Una cripta descargada se juega únicamente con lo de la caché (no se mezclan
versiones). Si una sala nunca se descargó, el juego no deja entrar en ella.

### Archivos que genera el programa

- `.cripta_cache/`: caché persistente (fichas, esqueleto, contenido, datos generales).
- `partidas/`: registros de partida (`*.log`, para `--replay`) y `puntajes.json`.
- `partidas/guardadas/`: partidas guardadas en formato binario propio (`*.bin`).

### Controles de la vista gráfica

- La interfaz se dibuja en un lienzo virtual de 800x450 y se escala a la
  ventana, así se ve con las mismas proporciones en cualquier computadora.
- La precarga de salas corre en segundo plano: cruzar una puerta no congela la
  ventana mientras llega la respuesta de la red.
- **F11**: pantalla completa. **Esc**: menú. **F1** o **/**: ayuda con todos los controles. **F2**: sonido.

## Documentación adicional

- [`docs/api.md`](docs/api.md): documentación del API de Cripta.
- [`docs/desiciones.md`](docs/desiciones.md): Documento de Decisiones de Diseño.
- [`PROMPTS_LLM.md`](PROMPTS_LLM.md): bitácora de prompts (§10.3).
