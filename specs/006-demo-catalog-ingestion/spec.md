# Spec 006: Demo Catalog Ingestion

## Objetivo funcional

Reemplazar la fuente demo actual (un único HTML con un único producto de precio fijo) por un
catálogo demo de varios productos con **capturas fechadas**, e implementar el flujo completo de
ingesta con capas explícitas:

```
acquisition -> parsing -> normalization -> validation
```

La fuente sigue siendo local y reproducible (sin red), pero se lee a través de la capa de
acquisition con la misma interfaz que un cliente HTTP, de forma que reemplazarla por una fuente
real solo implique cambiar el cliente y el parser.

## Criterios de aceptación

- Existe un catálogo demo ("demo-store") en `tests/fixtures/demo_store/<YYYY-MM-DD>/catalog.html`
  con al menos 3 capturas fechadas y unos 10 productos, que incluyen: cambios de precio entre
  capturas, un producto que se agota y vuelve, un producto nuevo en una captura posterior, un
  producto con disponibilidad desconocida, un producto sin marca y un ítem inválido (precio no
  numérico).
- **Acquisition**: existe un protocolo `ContentClient` (`get(location) -> str`) implementado por
  `HttpClient` (red) y por un nuevo `LocalFileClient` (archivos locales). Ambos traducen sus
  fallas a `AcquisitionError`. El spider recibe el cliente inyectado y no lee archivos por su
  cuenta.
- **Parsing**: `parse_catalog(html)` extrae, con XPath de `lxml`, los campos crudos de cada card
  de producto (`name`, `brand`, `price`, `currency`, `availability`, `product_url`, `image_url`).
  Devuelve strings (o `None` si falta un campo) y no valida. Lanza `ParsingError` solo si la
  página no tiene ninguna card (estructura inesperada).
- **Normalization**: funciones puras en `scraping/normalizers/product_normalizer.py` convierten
  el precio en formato `es-AR` (`"$ 45.999,90"`) a `Decimal`, el texto de disponibilidad a
  `Availability` (`in_stock`, `out_of_stock`, `unknown`) y limpian espacios en textos. Un precio
  que no puede interpretarse lanza `NormalizationError`.
- **Validation**: el modelo Pydantic `models.product.Product` incorpora `source`, `brand` y
  `captured_at`, y es el registro normalizado de una observación de producto (no se crea un
  modelo paralelo).
- **Errores por ítem**: un ítem que falla la normalización o la validación no aborta la captura;
  el spider devuelve los productos válidos y una lista de errores por ítem (tipo, mensaje, URL).
- El CLI `scrape-demo` procesa por defecto la captura más reciente, permite elegir una con
  `--capture YYYY-MM-DD`, muestra los errores por ítem y sigue exportando JSON/CSV y persistiendo
  con `--persist`.
- Tests sin red para: parser, normalizador, `LocalFileClient`, `HttpClient` (con
  `monkeypatch`), descubrimiento de capturas y spider sobre el catálogo con el ítem inválido.

## Fuera de alcance de esta spec

- Cambios al modelo de persistencia (enum de disponibilidad en snapshots, `captured_at` como
  `scraped_at`, idempotencia, `brand` persistido), registro de errores por ítem como
  `ScrapeError` e ingesta de todas las capturas en una corrida: se cubren en
  `007-historical-snapshots`.
- Fuentes HTTP reales, rate limiting y `robots.txt` (futuro, fuera de `v0.1.0`).
- Nuevas dependencias: se usa solo el stack existente (`requests`, `lxml`, `pydantic`).
