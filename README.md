# Cripta

Proyecto de Estructuras de Datos II — II Ciclo 2026.

Juego de mazmorra dirigido por eventos.

## Requisitos

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/) como gestor de entorno y dependencias

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

```bash
uv run python -m cripta
```

Esto debe mostrar el banner de bienvenida del juego.

## Estado actual del proyecto

En desarrollo. Por ahora solo está disponible el arranque del programa
(vista de bienvenida). Los comandos de juego, `--offline`, `--replay` y
`--bench` todavía no están implementados.

## Vista gráfica (Arcade)

El juego se juega en una ventana hecha con Arcade (ya no hay vista de consola Textual).

```bash
uv sync
uv run cripta            # en red
uv run cripta --offline  # con datos_prueba
```

- La interfaz se dibuja en un lienzo virtual de 800x450 y se escala a la
  ventana, así se ve con las mismas proporciones en cualquier computadora
  (laptop con escalado de Windows, monitor 1080p, 4K...). La ventana inicial
  se calcula según el tamaño de la pantalla y se puede redimensionar.
- **F11**: pantalla completa. **Esc**: menú. **F1** o **/**: ayuda con todos los controles.

## Documentación adicional

- [`docs/api.md`](docs/api.md): documentación del API de Cripta.
