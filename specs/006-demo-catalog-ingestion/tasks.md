# Tasks 006: Demo Catalog Ingestion

- [x] Crear el catálogo demo en `tests/fixtures/demo_store/` (3 capturas fechadas).
- [x] Agregar `AcquisitionError` y `NormalizationError` en `core/exceptions.py`.
- [x] Crear `ContentClient` (`scraping/clients/base.py`) y `LocalFileClient`
      (`scraping/clients/local_file_client.py`); `HttpClient` lanza `HttpClientError`, subclase
      de `AcquisitionError`.
- [x] Reemplazar `parse_product` por `parse_catalog` en `scraping/parsers/product_parser.py`.
- [x] Crear `scraping/normalizers/product_normalizer.py`.
- [x] Extender `models.product.Product` con `source`, `brand` y `captured_at`.
- [x] Reescribir `scraping/spiders/demo_store_spider.py` (`list_demo_captures`,
      `run_demo_spider` con errores por ítem).
- [x] Adaptar `services/scraping_service.py` y `cli.py` (`--catalog-dir`, `--capture`).
- [x] Tests: parser, normalizador, clientes, spider y persistencia sobre el catálogo.
- [x] Eliminar el fixture `demo_product_page.html`, que queda sin uso.
- [x] Actualizar `docs/02_architecture.md`, `docs/04_scraping_strategy.md` y las referencias al
      fixture viejo en `README.md`.
- [x] Verificar `make lint`, `make typecheck`, `make test` y `make run-demo`.
