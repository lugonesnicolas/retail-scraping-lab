# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Cada versión
enlaza las specs (`specs/`) que la componen.

## [Unreleased]

## [0.1.2] - 2026-09-26

Pulido de presentación para portfolio, sin cambios funcionales (`009-portfolio-release-polish`).

### Documentación

- `README.md` reescrito en inglés como engineering case study, con `v0.1.1` como versión actual.
- Screenshot real del dashboard en `docs/assets/dashboard-overview.png`, enlazado desde el README.
- Licencia MIT en `LICENSE`, coherente con `pyproject.toml`.
- `pyproject.toml`: descripción del paquete en inglés, igual que la del repositorio en GitHub.
- `docs/00_project_vision.md`: el alcance se presenta como el de `v0.1.1`.

## [0.1.1] - 2026-09-25

### Corregido

- El dashboard rompía con un `OperationalError` y un traceback de SQLAlchemy si se apuntaba a una
  base SQLite creada antes de `007-historical-snapshots` (cuando `product_snapshots.available`
  era un booleano en vez del `availability` actual). Como el proyecto no usa migraciones, esa
  situación es esperable al actualizar un clone existente; ahora se detecta antes de consultar y
  se muestra el mismo tipo de aviso que ya existía para "no existe la base" o "está vacía", con el
  comando `make reset-db` para recrearla.

## [0.1.0] - 2026-09-25

Primera versión completa: un vertical slice end-to-end de monitoreo de productos, precios y
disponibilidad, desde la adquisición hasta el dashboard.

### Ingesta (`006-demo-catalog-ingestion`)

- Fuente demo `demo-store`: catálogo local con tres capturas fechadas que incluyen cambios de
  precio, cambios de stock, un producto nuevo, disponibilidad desconocida y un ítem inválido.
- Capa de acquisition con el contrato `ContentClient`, implementado por `HttpClient` y
  `LocalFileClient`.
- Parser de catálogo con `lxml`/XPath, que devuelve texto crudo por producto.
- Normalizador de precios en formato `es-AR`, disponibilidad y textos.
- Modelo Pydantic `Product` como contrato de una observación (`source`, `captured_at`, `brand`,
  entre otros campos).
- Errores por ítem: un producto inválido se descarta y se reporta, sin abortar la captura.

### Persistencia histórica (`003-data-model`, `007-historical-snapshots`)

- Modelo SQLAlchemy sobre SQLite: `sources`, `products` (catálogo), `product_snapshots`
  (histórico), `scrape_runs` y `scrape_errors`.
- Snapshots fechados con la fecha de observación y carga idempotente por
  `UNIQUE(product_id, scraped_at)`.
- Disponibilidad guardada como enum de tres estados (`in_stock`, `out_of_stock`, `unknown`).
- Un run por captura con estado `success`, `partial` o `failed`, y errores persistidos.

### Analytics y dashboard (`005-dashboard`, `007-historical-snapshots`)

- `analytics/queries.py`: conteos, último snapshot por producto, precio promedio, disponibilidad,
  variación de precio (window function), historial, corridas y errores.
- Dashboard Streamlit con las secciones Overview, Latest products, Price changes, Price history,
  Scrape runs y Errors.

### Developer experience y CI (`001`, `004`, `008-release-v0.1.0`)

- CLI Typer (`scrape-demo`, `init-db [--reset]`) y Makefile (`install`, `run-demo`, `dashboard`,
  `check`, `reset-db`).
- GitHub Actions: `ci.yml` (ruff, formato, mypy, pytest) y `scrape.yml` (pipeline completo, con
  los exports y la base SQLite como artefacto).
- README reescrito como case study.

### Corregido

- Una falla al persistir hacía rollback también del run fallido y de su error, así que no quedaba
  registro. Ahora el run se crea en su propia transacción y la falla queda registrada.

### Cambios de esquema

- `product_snapshots.available` (bool) pasa a `availability` (texto), y se agregan
  `scrape_runs.snapshots_skipped` y la restricción única de snapshots. No hay migraciones: una
  base local creada con una versión anterior se recrea con `make reset-db`.
