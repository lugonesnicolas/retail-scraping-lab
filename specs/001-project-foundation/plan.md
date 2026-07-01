# Plan 001: Project Foundation

## Enfoque técnico

1. **Estructura de carpetas**: crear todas las carpetas descritas en `docs/02_architecture.md`
   de una sola vez, con archivos `__init__.py` vacíos en cada subpaquete de
   `src/retail_scraping_lab/` y `.gitkeep` en las carpetas de `data/` que deben existir pero no
   versionar contenido.

2. **Configuración de Python**: definir `pyproject.toml` con:
   - `requires-python = ">=3.12"`.
   - Dependencias de runtime: `requests`, `lxml`, `pydantic`, `pydantic-settings`, `sqlalchemy`,
     `typer`, `rich`, `streamlit`, `pandas`.
   - Dependencias de desarrollo (`[project.optional-dependencies].dev`): `pytest`, `ruff`,
     `mypy`, `types-requests`.
   - Configuración de `ruff` (línea 100, reglas E/F/W/I/UP/B/SIM/N, target `py312`).
   - Configuración de `mypy` en modo razonable: `check_untyped_defs = true`,
     `disallow_untyped_defs = false` (no forzar tipado exhaustivo todavía),
     `ignore_missing_imports = true` para no bloquear por stubs faltantes de librerías de
     terceros.
   - Configuración de `pytest` (`testpaths = ["tests"]`).

3. **Makefile**: comandos `install`, `lint`, `format`, `typecheck`, `test`, `run-demo`,
   `dashboard`, cada uno delegando en la herramienta correspondiente (`pip`, `ruff`, `mypy`,
   `pytest`, `python -m retail_scraping_lab.cli`, `streamlit run`).

4. **Configuración de aplicación**: `config/settings.py` con una clase `Settings` basada en
   `pydantic-settings`, leyendo variables con prefijo `RSL_` desde `.env`, reflejando las
   variables documentadas en `.env.example`.

5. **Core transversal**: `core/logging.py` con una función `configure_logging()` que use
   `rich.logging.RichHandler`; `core/exceptions.py` con una jerarquía mínima de excepciones de
   dominio (`ScrapingError`, `HttpClientError`, `ParsingError`, `ValidationError` propia si hace
   falta distinguirla de la de Pydantic).

6. **Skeletons de negocio**: crear los módulos de `scraping/`, `models/`, `repositories/`,
   `services/`, `analytics/` y `cli.py` con la interfaz mínima funcional descrita en las specs
   `002-product-scraper` y `003-data-model` (implementación real ocurre en esas specs; aquí solo
   se asegura que el módulo exista, importe y tenga docstring/type hints básicos).

7. **Dashboard skeleton**: `dashboard/app.py` mínimo, funcional, leyendo un archivo de ejemplo
   (se completa en `005-dashboard`).

8. **Tests skeleton**: fixture HTML mínima y un test por módulo clave, sin dependencia de red.

9. **GitHub Actions skeleton**: `ci.yml` (install + ruff + mypy + pytest) y `scrape.yml`
   (`workflow_dispatch`, ejecuta `make run-demo`, sube artefactos de `data/exports/`).

10. **Documentación**: escribir todos los documentos de `docs/`, los ADRs iniciales, `CLAUDE.md`,
    `AGENTS.md` y `README.md`, y las carpetas de specs `002` a `005` con su `spec.md`, `plan.md`
    y `tasks.md` (menos desarrollados que esta spec, sirviendo como punto de partida).

## Orden de ejecución

El orden sigue, a grandes rasgos, el de esta lista: primero estructura y configuración, luego
código transversal (config/core), luego skeletons de negocio, luego tests, CI y documentación.
Este orden minimiza el riesgo de tener que reestructurar carpetas después de escribir código.
