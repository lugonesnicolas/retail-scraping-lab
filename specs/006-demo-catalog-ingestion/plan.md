# Plan 006: Demo Catalog Ingestion

## Enfoque técnico

- **Fixtures** (`tests/fixtures/demo_store/`): un directorio por captura (`2026-09-01`,
  `2026-09-08`, `2026-09-15`), cada uno con un `catalog.html` estático que lista cards
  `<article class="product-card">`. El nombre del directorio es la fecha de la captura; se
  mantiene la convención existente de fixtures en `tests/fixtures/` (el CLI ya usaba esa ruta
  como fuente demo por defecto).
- **Acquisition** (`scraping/clients/`):
  - `base.py`: `ContentClient`, un `typing.Protocol` con `get(location, /) -> str`. Es
    estructural, así que `HttpClient` lo cumple sin heredar nada.
  - `local_file_client.py`: `LocalFileClient(base_dir)` lee `base_dir / location` y traduce
    `OSError` a `AcquisitionError`.
  - `core/exceptions.py`: se agrega `AcquisitionError` como base de `HttpClientError`, y
    `NormalizationError`.
- **Parsing** (`scraping/parsers/product_parser.py`): `parse_catalog(html) -> list[RawProduct]`,
  donde `RawProduct = dict[str, str | None]`. XPath absoluto para encontrar las cards y relativo
  (`.//...`) para los campos de cada card. Reemplaza a `parse_product` (página de producto
  único), que queda sin uso junto con su fixture `demo_product_page.html`.
- **Normalization** (`scraping/normalizers/product_normalizer.py`):
  - `clean_text(value)`: colapsa espacios y devuelve `None` si queda vacío.
  - `parse_price(value)`: formato explícito `es-AR`: se descarta el símbolo de moneda, `.` son
    miles y `,` es el separador decimal. No intenta adivinar formatos: la fuente declara el suyo.
  - `normalize_availability(value)`: mapeo de textos conocidos (`"En stock"`, `"Sin stock"`,
    …) a `Availability`. Cualquier otro texto, o su ausencia, es `unknown`.
  - `normalize_product(raw, *, source, captured_at) -> dict`: arma el payload para Pydantic.
    Los campos faltantes quedan en `None` y es Pydantic quien decide si son obligatorios.
- **Validation** (`models/product.py`): `Product` suma `source: str`, `brand: str | None` y
  `captured_at: datetime`. Los nombres existentes se mantienen (`name`, `product_url`) para no
  romper el resto del código.
- **Spider** (`scraping/spiders/demo_store_spider.py`):
  - `DemoCapture(captured_at, location)` y `list_demo_captures(catalog_dir)`: descubren las
    capturas por nombre de directorio, ordenadas cronológicamente. El conocimiento de cómo está
    organizada la fuente vive en el spider de esa fuente.
  - `run_demo_spider(client, capture) -> SpiderResult(products, errors)`: `client.get` →
    `parse_catalog` → por cada ítem, `normalize_product` → `Product.model_validate`. Un
    `NormalizationError` o un `ValidationError` se convierten en `ItemError` y la captura sigue.
- **Service** (`services/scraping_service.py`): `run_demo_scraping(catalog_dir, output_dir, *,
  capture_date=None, persist=False, session_factory=None) -> DemoScrapeResult` elige la captura
  (la última por defecto), arma el `LocalFileClient`, corre el spider, exporta y, si se pide,
  persiste. En esta spec la persistencia no cambia de semántica (ver `007`).
- **CLI** (`cli.py`): `scrape-demo --catalog-dir --capture --persist`. Muestra la tabla de
  productos (con marca) y, si los hay, la tabla de errores por ítem.
- **Tests**: `tests/unit/test_product_parser.py` (reescrito), `test_product_normalizer.py`,
  `test_clients.py`; `tests/integration/test_scraping_pipeline.py` y
  `test_persistence_pipeline.py` adaptados al catálogo.

## Decisiones

- **Normalizar antes de validar**: el parser entrega texto crudo, el normalizador lo lleva a
  tipos del dominio y Pydantic valida el contrato final. Así Pydantic no necesita saber del
  formato de precios de cada fuente, y el normalizador se testea como funciones puras.
- **Errores por ítem, no por página**: una fuente real casi siempre trae algún ítem mal formado;
  descartar la captura entera por un ítem perdería datos válidos. La página completa solo falla
  si no se pudo encontrar ninguna card (señal de que cambió la estructura del sitio).
