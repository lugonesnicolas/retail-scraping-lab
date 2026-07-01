# Arquitectura

## Capas del proyecto

El proyecto está organizado en capas con responsabilidades bien separadas, todas dentro de
`src/retail_scraping_lab/`:

```
scraping.clients   -> obtiene HTML/XML crudo desde una fuente (HTTP o fixture local)
scraping.parsers   -> convierte HTML crudo en datos estructurados (dicts) usando lxml
models             -> valida y tipa esos datos estructurados con Pydantic; define el esquema SQLAlchemy
scraping.pipelines -> orquesta parser + validación y exporta/persiste los productos
repositories       -> encapsula el acceso a la base de datos (SQLAlchemy)
services           -> coordina spiders, pipelines y repositorios para un caso de uso completo
analytics          -> consultas de negocio sobre los datos ya persistidos
cli                -> expone comandos (typer) para ejecutar el scraper demo y otras acciones
dashboard/         -> aplicación Streamlit que lee datos exportados/persistidos y los visualiza
```

## Responsabilidad de cada carpeta

- **`scraping/clients/`**: solo sabe cómo hacer una request HTTP (con `requests`) y devolver el
  contenido crudo. No sabe nada de HTML ni de productos.
- **`scraping/parsers/`**: solo sabe cómo tomar HTML crudo y extraer campos específicos con
  `lxml` (XPath). No sabe hacer requests ni valida tipos de datos.
- **`scraping/spiders/`**: combina un cliente y un parser para una fuente concreta (por ejemplo,
  `demo_store_spider.py`), produciendo una lista de productos parseados (dicts).
- **`models/`**: define `Product` (Pydantic) como esquema de validación de un producto parseado,
  y `database.py` como base de SQLAlchemy para la futura persistencia.
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
Fixture HTML / sitio demo
        |
        v
 scraping.clients.http_client   (obtiene HTML crudo)
        |
        v
 scraping.parsers.product_parser (HTML -> dict con campos crudos)
        |
        v
 models.product.Product          (dict -> Product validado con Pydantic)
        |
        v
 scraping.pipelines.product_pipeline (lista de Product -> JSON/CSV, y en el futuro -> repositorio)
        |
        v
 repositories.product_repository  (persistencia en SQLAlchemy, base a futuro)
        |
        v
 analytics.queries / dashboard/app.py  (lectura y visualización)
```

## Por qué se separan cliente, parser, pipeline, repositorio y dashboard

- **Testabilidad**: el parser se puede testear con un fixture HTML local, sin red. El pipeline se
  puede testear con productos ya parseados, sin HTML. El dashboard se puede probar con datos de
  ejemplo, sin scraper.
- **Reemplazabilidad**: si en el futuro se scrapea un sitio real distinto, solo cambia el spider
  (cliente + parser específicos); el pipeline, el modelo y el dashboard no se modifican.
- **Claridad**: cada módulo tiene una sola responsabilidad, lo que facilita explicar el proyecto
  en una entrevista o en un post técnico, y facilita que un agente de IA trabaje sobre una capa
  sin romper las demás.
- **Evolución incremental**: permite avanzar por etapas (spec por spec) sin tener que rediseñar
  la estructura general del proyecto en cada paso.
