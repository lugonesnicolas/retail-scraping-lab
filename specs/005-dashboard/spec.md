# Spec 005: Dashboard

## Objetivo funcional

Construir un dashboard en Streamlit que permita visualizar el estado histórico real de los
productos scrapeados, leyendo desde la base SQLite persistida por `003-data-model` (no solo el
último export JSON/CSV), respondiendo de forma visual las preguntas de
`docs/05_business_questions.md` que ya están soportadas por el modelo de datos.

## Iteración 1 (completada, ver historial de `git`)

- `dashboard/app.py` leía un archivo CSV/JSON generado por el pipeline (`data/exports/`) usando
  `pandas`, y mostraba cantidad de productos, precio promedio, tabla de productos y disponibilidad.

## Iteración 2 (esta spec): lectura desde SQLite

### Criterios de aceptación

- `src/retail_scraping_lab/analytics/queries.py` expone funciones de solo lectura, sobre una
  `Session` de SQLAlchemy ya abierta, para: total de productos, total de snapshots, último
  snapshot por producto, precio promedio actual, disponibilidad actual, historial de precio por
  producto, últimas corridas de scraping y errores recientes.
- `dashboard/app.py` lee la base de datos configurada en `RSL_DATABASE_URL` (vía
  `config/settings.py`), no el export JSON/CSV.
- Si la base de datos no existe, el dashboard no rompe: muestra un aviso claro con las
  instrucciones (`make init-db`, `scrape-demo --persist`) para generarla.
- Si la base existe pero no tiene productos, muestra un aviso específico sugiriendo correr
  `scrape-demo --persist`.
- El dashboard muestra, como mínimo, las secciones: Overview (total de productos, total de
  snapshots, precio promedio actual, disponibles/no disponibles), Latest products (tabla con
  último precio por producto), Price history (selector de producto + gráfico de evolución),
  Scrape runs (últimas corridas y su estado) y Errors (errores recientes, si existen).
- El flujo de export JSON/CSV (`scrape-demo` sin `--persist`, `pipelines/product_pipeline.py`) no
  se modifica ni se rompe.
- El dashboard corre localmente con `make dashboard` sin errores, usando datos de ejemplo
  generados por `python -m retail_scraping_lab.cli scrape-demo --persist`.

## Fuera de alcance de esta spec

- Autenticación o control de acceso.
- Comparar dos corridas de scraping puntuales, o agrupar variación de precio por categoría (ver
  preguntas pendientes en `docs/05_business_questions.md`).
- Despliegue del dashboard en un servicio externo.
- Migraciones de esquema (Alembic) o cambios al modelo de datos de `003-data-model`.
