# Plan 007: Historical Snapshots

## Enfoque técnico

- **Modelo** (`models/database.py`):
  - `ProductSnapshot.available: bool` pasa a `availability: str` (valores de
    `models.product.Availability`).
  - El índice `(product_id, scraped_at)` se reemplaza por un `UniqueConstraint` sobre las mismas
    columnas: en SQLite crea igualmente un índice, así que las consultas históricas no pierden
    rendimiento, y además garantiza la idempotencia de la carga.
  - `ScrapeRun` suma `snapshots_skipped`.
  - `reset_db(engine)` hace `drop_all` + `create_all`, y el CLI lo expone como
    `init-db --reset`.
- **Repositorio** (`repositories/product_repository.py`):
  - `save_scraped_products` usa `captured_at` como `scraped_at`, omite snapshots que ya existen
    (`snapshot_exists`) y devuelve un `SaveResult(inserted, updated, skipped)` en lugar de una
    tupla.
  - `get_or_create_product` persiste y actualiza `brand`.
- **Service** (`services/scraping_service.py`):
  - `scrape_capture`: corre el spider y traduce `AcquisitionError`/`ParsingError` a un error de
    captura, sin abortar el resto.
  - `_persist_capture`: usa transacciones separadas.
    1. Se crea el run y se commitea, para que exista aunque todo lo demás falle.
    2. Se guardan snapshots y errores y se cierra el run en una segunda transacción.
    3. Si esa segunda transacción falla, después del rollback se registra el run `failed` con su
       error en una tercera, y recién entonces se propaga la excepción. Así se corrige la
       pérdida del error por el rollback.
  - `run_demo_scraping` procesa todas las capturas (o una) y devuelve un `CaptureResult` por
    captura.
- **Export**: `export_products` acepta un `filename_stem` opcional. El servicio exporta cada
  captura como `demo-store_<fecha>.json`: el nombre es determinístico, así que reprocesar
  sobrescribe el mismo archivo (coherente con la idempotencia de la base) y varias capturas
  procesadas en el mismo segundo no colisionan.
- **Analytics** (`analytics/queries.py`):
  - `LatestProductRow` suma `source_name`, `brand`, `product_url` y `availability`.
  - `current_availability_breakdown` devuelve los 3 estados.
  - Nueva `price_changes`: usa la window function `row_number() OVER (PARTITION BY product_id
    ORDER BY scraped_at DESC)` para tomar las dos observaciones más recientes de cada producto,
    y devuelve las que cambiaron de precio, con variación absoluta y porcentual.
- **Dashboard**: agrega columnas, la sección "Price changes" y el rótulo UTC. Solo llama a
  `analytics.queries`, sin lógica propia.
- **Makefile**: `run-demo` pasa a `scrape-demo --persist`; se agregan `reset-db`
  (`init-db --reset`) y `check` (lint + typecheck + test).

## Decisiones

- **`scraped_at` = fecha de captura**: el histórico tiene que reflejar cuándo se observó el dato
  en la fuente, no cuándo se cargó. Para una fuente HTTP en vivo ambos coinciden; para capturas
  guardadas, no. El momento de ejecución queda en `scrape_runs.started_at`.
- **Idempotencia por restricción única y no solo por lógica de aplicación**: la base garantiza
  la invariante aunque otro proceso cargue datos, y el repositorio consulta antes de insertar
  para contar los omitidos sin depender de capturar `IntegrityError`.
- **Sin Alembic**: el proyecto no tiene datos productivos que migrar. Recrear la base local
  (`make reset-db`) es suficiente y está documentado.
