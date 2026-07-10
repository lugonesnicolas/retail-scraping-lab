# Tasks 003: Data Model

- [x] Definir modelos ORM (`Source`, `Category`, `Product`, `ProductSnapshot`, `ScrapeRun`,
      `ScrapeError`) en `models/database.py`, con constraints (`Source.name` único,
      `(source_id, product_url)` único en `Product`) e índices (`scraped_at`, `product_id`,
      `source_id`).
- [x] Implementar `get_engine`, `get_session_factory`, `init_db` y `get_session`.
- [x] Implementar `repositories/product_repository.py`: `get_or_create_source`,
      `get_or_create_product`, `create_product_snapshot`, `create_scrape_run`,
      `finish_scrape_run`, `create_scrape_error`, `save_scraped_products`.
- [x] Conectar `services/scraping_service.py` (flag `persist`) manteniendo el export JSON/CSV.
- [x] Agregar comandos CLI `init-db` y `scrape-demo --persist`; ajustar `Makefile`
      (`run-demo` invoca `scrape-demo` explícitamente, se agrega target `init-db`).
- [x] Escribir tests con SQLite en memoria/temporal: creación de tablas, alta de
      fuente/producto/snapshot, no-duplicación por `source_id`+`product_url`, y guardado de
      productos parseados desde el fixture local (`tests/unit/test_database.py`,
      `tests/unit/test_product_repository.py`, `tests/integration/test_persistence_pipeline.py`).
- [x] Documentar en `docs/03_data_model.md` el modelo final, la diferencia `Product` vs
      `ProductSnapshot`, por qué histórico, por qué SQLite, y qué queda pendiente (Alembic, otro
      motor de base de datos).
