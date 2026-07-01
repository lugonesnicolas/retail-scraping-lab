# Spec 002: Product Scraper

## Objetivo funcional

Implementar un flujo de scraping demo que obtenga HTML (desde un fixture local, y opcionalmente
un sitio de demostración), extraiga datos de producto y los valide, produciendo una lista de
productos listos para exportar. Ver `docs/04_scraping_strategy.md` para el contexto completo de
la estrategia de scraping.

## Criterios de aceptación

- Existe un cliente HTTP (`scraping/clients/http_client.py`) implementado con `requests`, con:
  - timeout configurable (vía `config/settings.py`);
  - headers básicos, incluyendo `User-Agent` configurable;
  - manejo simple de errores (excepciones propias de `core/exceptions.py` ante fallas de red o
    status code de error);
  - diseño que permita agregar retries en el futuro sin cambiar su interfaz pública;
  - separación clara: el cliente solo obtiene contenido crudo, no parsea HTML.
- Existe un parser de producto (`scraping/parsers/product_parser.py`) implementado con `lxml`,
  usando XPath (o mecanismos equivalentes de `lxml`) para extraer, desde HTML:
  - `name`
  - `price`
  - `currency`
  - `availability`
  - `product_url`
  - `image_url`
- El parser está separado del cliente HTTP: recibe HTML como string/bytes, no hace requests.
- Existe un modelo Pydantic `Product` (`models/product.py`) que valida los campos extraídos por
  el parser (tipos, presencia de campos obligatorios, precio numérico no negativo).
- Existe un pipeline (`scraping/pipelines/product_pipeline.py`) que recibe una lista de
  `Product` ya validados y los exporta a JSON y/o CSV en `data/exports/`.
- Existe un spider demo (`scraping/spiders/demo_store_spider.py`) que combina cliente + parser
  para procesar el fixture local `tests/fixtures/demo_product_page.html`.
- Existe un comando CLI (`cli.py`, comando `scrape-demo`) que ejecuta el spider demo end-to-end
  y deja un archivo de export en `data/exports/`.
- Los tests (`tests/unit/test_product_parser.py`, `tests/integration/test_scraping_pipeline.py`)
  no dependen de acceso a internet: usan el fixture local.

## Requisitos técnicos explícitos

- Cliente HTTP: `requests`.
- Parser HTML: `lxml`.
- Extracción de datos: XPath (o selectores compatibles con `lxml`, como CSS-a-XPath vía
  `lxml.cssselect` si se justifica), nunca `beautifulsoup4`.
- Validación de datos: Pydantic.
- Tests: `pytest`, usando fixture local (`tests/fixtures/demo_product_page.html`), sin
  dependencia de internet.

## Fuera de alcance de esta spec

- Persistencia en base de datos (se cubre en `003-data-model`).
- Scraping de un sitio real de producción.
- Rate limiting y retries avanzados (se documentan como extensión futura en
  `docs/04_scraping_strategy.md`).
