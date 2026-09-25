# Arquitectura

## Capas del proyecto

El proyecto está organizado en capas con responsabilidades bien separadas, todas dentro de
`src/retail_scraping_lab/`:

```
scraping.clients     -> acquisition: obtiene contenido crudo (HTTP o archivo local), sin interpretarlo
scraping.parsers     -> parsing: convierte HTML crudo en campos de texto (dicts) usando lxml/XPath
scraping.normalizers -> normalization: convierte esos textos a valores del dominio (Decimal, enums)
models               -> validation: contrato Pydantic de un producto; define el esquema SQLAlchemy
scraping.spiders     -> combina las capas anteriores para una fuente concreta, producto por producto
scraping.pipelines   -> exporta productos ya validados (JSON/CSV)
repositories       -> encapsula el acceso a la base de datos (SQLAlchemy)
services           -> coordina spiders, pipelines y repositorios para un caso de uso completo
analytics          -> consultas de negocio sobre los datos ya persistidos
cli                -> expone comandos (typer) para ejecutar el scraper demo y otras acciones
dashboard/         -> aplicación Streamlit que lee datos exportados/persistidos y los visualiza
```

## Responsabilidad de cada carpeta

- **`scraping/clients/`**: capa de acquisition. Define el contrato `ContentClient`
  (`get(location) -> str`), implementado por `HttpClient` (`requests`) y por `LocalFileClient`
  (archivos locales, usado por la fuente demo). Solo devuelve contenido crudo: no sabe nada de
  HTML ni de productos, y reporta sus fallas como `AcquisitionError`.
- **`scraping/parsers/`**: solo sabe cómo tomar HTML crudo y extraer campos de texto con `lxml`
  (XPath). No hace requests, no convierte tipos y no decide qué campos son obligatorios; un
  campo ausente queda en `None`.
- **`scraping/normalizers/`**: funciones puras que llevan los textos del parser a valores del
  dominio (precio en formato `es-AR` a `Decimal`, texto de disponibilidad a `Availability`,
  limpieza de espacios). Un valor que no se puede interpretar lanza `NormalizationError`.
- **`scraping/spiders/`**: combina cliente, parser, normalizador y validación para una fuente
  concreta (por ejemplo, `demo_store_spider.py`). Recibe el cliente inyectado y procesa cada
  producto de forma independiente: un ítem inválido se reporta como error sin descartar el resto.
- **`models/`**: define `Product` (Pydantic) como contrato de una observación de producto ya
  normalizada (fuente, fecha de captura, nombre, marca, precio, moneda, disponibilidad, URLs), y
  `database.py` con el esquema de persistencia de SQLAlchemy.
- **`scraping/pipelines/`**: recibe productos ya validados y los exporta (JSON/CSV) o los envía
  a un repositorio. No sabe scrapear ni parsear.
- **`repositories/`**: encapsula el acceso a la base de datos. Es la única capa que debería
  hablar SQL/SQLAlchemy directamente para lectura/escritura de productos.
- **`services/`**: orquesta un caso de uso completo (por ejemplo, "correr el scraper demo y
  exportar resultados"), combinando spider + pipeline + repositorio.
- **`analytics/`**: consultas de solo lectura pensadas para responder preguntas de negocio
  (ver `docs/05_business_questions.md`), usadas por el dashboard o por la CLI.
- **`config/`**: configuración de la aplicación vía `pydantic-settings`, leyendo variables de
  entorno (`.env`).
- **`core/`**: utilidades transversales: logging (`rich`) y excepciones propias del dominio.
- **`dashboard/`**: aplicación Streamlit independiente, que consume datos ya generados (CSV/JSON
  o base de datos), sin lógica de scraping propia.

## Flujo de datos

```
Catálogo demo (tests/fixtures/demo_store/<fecha>/catalog.html)
        |
        v
 scraping.clients (LocalFileClient | HttpClient)   acquisition: contenido crudo
        |
        v
 scraping.parsers.product_parser                    parsing: HTML -> campos de texto por producto
        |
        v
 scraping.normalizers.product_normalizer            normalization: texto -> Decimal / enums
        |
        v
 models.product.Product                             validation: contrato Pydantic
        |
        +--> scraping.pipelines.product_pipeline     export JSON/CSV
        |
        v
 repositories.product_repository                    persistencia histórica (SQLAlchemy/SQLite)
        |
        v
 analytics.queries -> dashboard/app.py               lectura y visualización
```

## Por qué se separan cliente, parser, pipeline, repositorio y dashboard

- **Testabilidad**: el parser se puede testear con un fixture HTML local, sin red; el
  normalizador, como funciones puras con casos parametrizados. El pipeline se
  puede testear con productos ya parseados, sin HTML. El dashboard se puede probar con datos de
  ejemplo, sin scraper.
- **Reemplazabilidad**: si en el futuro se scrapea un sitio real distinto, solo cambia el spider
  (cliente + parser específicos); el pipeline, el modelo y el dashboard no se modifican.
- **Claridad**: cada módulo tiene una sola responsabilidad, lo que facilita explicar el proyecto
  en una entrevista o en un post técnico, y facilita que un agente de IA trabaje sobre una capa
  sin romper las demás.
- **Evolución incremental**: permite avanzar por etapas (spec por spec) sin tener que rediseñar
  la estructura general del proyecto en cada paso.
