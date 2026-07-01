# Spec 003: Data Model

## Objetivo funcional

Implementar la base de persistencia relacional del proyecto usando SQLAlchemy, reflejando el
modelo de datos propuesto en `docs/03_data_model.md`, y un repositorio mínimo para leer y
escribir productos.

## Criterios de aceptación

- `models/database.py` define la base declarativa de SQLAlchemy y los modelos ORM para
  `Source`, `Category`, `Product`, `ProductSnapshot`, `ScrapeRun` y `ScrapeError`, con las
  relaciones descritas en `docs/03_data_model.md`.
- La conexión a base de datos usa SQLite por defecto (ver `docs/adr/0003-use-sqlite-first.md`),
  con la URL configurable vía `Settings` (`RSL_DATABASE_URL`).
- `repositories/product_repository.py` expone operaciones mínimas: crear/obtener una fuente,
  crear/obtener un producto por `external_id` + `source_id`, y registrar un `product_snapshot`
  asociado a un `scrape_run`.
- Existe una forma de inicializar el esquema (crear las tablas) de forma explícita, sin
  necesidad de un sistema de migraciones completo en esta etapa.
- Los modelos ORM y el modelo Pydantic `Product` (de la spec `002`) están claramente separados:
  el primero es de persistencia, el segundo de validación de datos scrapeados.

## Fuera de alcance de esta spec

- Sistema de migraciones (Alembic u otro): se evaluará si el proyecto lo necesita en una etapa
  posterior.
- Persistencia productiva contra PostgreSQL u otro motor distinto de SQLite.
- Integración completa del pipeline de scraping con el repositorio (el pipeline de `002` exporta
  a archivo; conectar ambos flujos es una extensión futura, documentable como spec adicional si
  se decide abordarla).
