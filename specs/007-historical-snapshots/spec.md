# Spec 007: Historical Snapshots

## Objetivo funcional

Convertir la ingesta del catálogo demo (`006-demo-catalog-ingestion`) en un histórico confiable
y consultable: cada captura se persiste como una observación fechada de cada producto,
reprocesar una captura no duplica datos, los errores quedan registrados y el dashboard responde
cómo cambió cada producto respecto de su observación anterior.

## Criterios de aceptación

- **Disponibilidad sin pérdida de información**: `product_snapshots.availability` guarda el enum
  (`in_stock`, `out_of_stock`, `unknown`) en lugar de un booleano.
- **Fecha de observación**: el `scraped_at` de cada snapshot es el `captured_at` del producto
  (la fecha de la captura), no el momento en que se corrió el comando. `scrape_runs.started_at`
  sigue siendo el momento real de ejecución.
- **Idempotencia**: existe una restricción única `(product_id, scraped_at)`. Reprocesar una
  captura ya cargada no crea snapshots nuevos; se cuentan como `snapshots_skipped` en el run.
- **Catálogo actualizado**: el repositorio persiste `brand` y actualiza nombre, marca e imagen de
  productos existentes con el último valor observado.
- **Un run por captura**, con estado:
  - `success`: todos los ítems válidos;
  - `partial`: hay productos válidos y errores por ítem;
  - `failed`: no hay ningún producto válido (por ejemplo, falla de acquisition o de parsing).
- **Errores persistidos**: cada error por ítem o de página se guarda como `ScrapeError` asociado
  al run. Si la persistencia falla de forma inesperada, el run queda `failed` con su error
  registrado (hoy ambos se pierden por el rollback).
- **CLI**: `scrape-demo` procesa todas las capturas en orden cronológico (o una con
  `--capture`) y muestra un resumen por captura. `init-db --reset` recrea el esquema.
- **Makefile**: `make run-demo` corre el flujo completo con persistencia; se agregan
  `make reset-db` y `make check`.
- **Analytics y dashboard**:
  - la tabla de últimos productos muestra fuente, marca, URL y disponibilidad (3 estados);
  - la disponibilidad actual se desglosa en los 3 estados;
  - existe una consulta de variación de precio (última observación vs. anterior, con variación
    absoluta y porcentual), visible en el dashboard;
  - las fechas se rotulan como UTC.
- **Tests** sin red:
  - integración de las 3 capturas;
  - idempotencia;
  - run `partial` con error persistido;
  - regresión del rollback;
  - CLI con `CliRunner`;
  - smoke test del dashboard con `AppTest`.

## Fuera de alcance de esta spec

- Migraciones de esquema (Alembic). El cambio de esquema requiere recrear la base local
  (`make reset-db`); se documenta.
- Fuentes HTTP reales, categorías y preguntas analíticas por categoría.
