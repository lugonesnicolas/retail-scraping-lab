# Spec 003: Data Model

## Objetivo funcional

Implementar la base de persistencia relacional del proyecto usando SQLAlchemy, reflejando el
modelo de datos documentado en `docs/03_data_model.md`, un repositorio para leer y escribir
productos/snapshots, y conectar (de forma opcional) el flujo de scraping demo con esa
persistencia.

## Criterios de aceptación

- [x] `models/database.py` define la base declarativa de SQLAlchemy y los modelos ORM para
      `Source`, `Category`, `Product`, `ProductSnapshot`, `ScrapeRun` y `ScrapeError`, con las
      relaciones, constraints e índices descritos en `docs/03_data_model.md`.
- [x] La conexión a base de datos usa SQLite por defecto (ver `docs/adr/0003-use-sqlite-first.md`),
      con la URL configurable vía `Settings` (`RSL_DATABASE_URL`, ver `.env.example`).
- [x] `repositories/product_repository.py` expone operaciones mínimas: `get_or_create_source`,
      `get_or_create_product` (deduplicado por `source_id` + `product_url`),
      `create_product_snapshot`, `create_scrape_run`, `finish_scrape_run`, `create_scrape_error`
      y `save_scraped_products` (guarda una lista de productos parseados como snapshots).
- [x] Existe una forma de inicializar el esquema (`init_db`, comando `init-db` del CLI), sin
      necesidad de un sistema de migraciones completo en esta etapa.
- [x] Los modelos ORM y el modelo Pydantic `Product` (de la spec `002`) están claramente
      separados: el primero es de persistencia, el segundo de validación de datos scrapeados.
- [x] `services/scraping_service.py` y `cli.py` permiten correr el demo con o sin persistencia
      (`scrape-demo --persist`), manteniendo el export a JSON/CSV existente.
- [x] Tests con SQLite en memoria/temporal cubren creación de tablas, alta de fuente/producto,
      snapshot, no-duplicación de producto por fuente+URL, y guardado desde el fixture local.

## Fuera de alcance de esta spec

- Sistema de migraciones (Alembic u otro): se evaluará si el proyecto lo necesita en una etapa
  posterior (ver sección "Qué queda para una etapa futura" en `docs/03_data_model.md`).
- Persistencia productiva contra PostgreSQL u otro motor distinto de SQLite.
- Integración con fuentes reales (Scrapy, Playwright, `httpx`, `beautifulsoup4`): el stack de
  scraping sigue siendo `requests` + `lxml` sobre fixtures locales.
