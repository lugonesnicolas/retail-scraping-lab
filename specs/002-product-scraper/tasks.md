# Tasks 002: Product Scraper

- [x] Implementar `HttpClient` en `scraping/clients/http_client.py` con timeout, headers y
      manejo de errores.
- [x] Implementar `parse_product` en `scraping/parsers/product_parser.py` con XPath.
- [x] Implementar modelo `Product` en `models/product.py` con Pydantic.
- [x] Implementar `run_demo_spider` en `scraping/spiders/demo_store_spider.py`.
- [x] Implementar `export_products` en `scraping/pipelines/product_pipeline.py` (JSON y CSV).
- [x] Implementar comando `scrape-demo` en `cli.py`.
- [x] Crear fixture `tests/fixtures/demo_product_page.html`.
- [x] Escribir `tests/unit/test_product_parser.py`.
- [x] Escribir `tests/integration/test_scraping_pipeline.py`.
- [x] Ejecutar `make run-demo` y verificar que se genera un archivo en `data/exports/`.
- [x] Ejecutar `make test` y verificar que todos los tests pasan sin acceso a internet.
