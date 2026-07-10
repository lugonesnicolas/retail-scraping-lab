# Modelo de datos

Implementado en `src/retail_scraping_lab/models/database.py` (spec `003-data-model`, ver
`specs/003-data-model/`). El diseño separa el "catálogo" (qué producto es) de los "snapshots"
(cómo estaba ese producto en un momento dado), para poder responder preguntas históricas como
"cómo evolucionó el precio de este producto" sin perder información en cada scrape.

## Entidades

### `sources`

Representa una fuente de datos (un sitio o fixture de donde se obtienen productos).

| Campo         | Tipo      | Descripción                                       |
|---------------|-----------|-----------------------------------------------------|
| id            | int (PK)  | Identificador interno.                               |
| name          | str       | Nombre de la fuente (único, ej. "demo-store").       |
| base_url      | str       | URL base o identificador de la fuente.               |
| source_type   | str       | Tipo de fuente (ej. "fixture", "http").              |
| active        | bool      | Si la fuente está habilitada para scrapear.          |
| created_at    | datetime  | Fecha de alta.                                       |
| updated_at    | datetime  | Última actualización.                                |

### `categories`

Categoría de producto, propia del dominio del proyecto (no necesariamente igual a la de la
fuente original).

| Campo         | Tipo               | Descripción                                |
|---------------|--------------------|-----------------------------------------------|
| id            | int (PK)           | Identificador interno.                        |
| source_id     | int (FK)           | Fuente a la que pertenece la categoría.       |
| name          | str                | Nombre de la categoría.                       |
| url           | str (nullable)     | URL de la categoría en la fuente.             |
| external_id   | str (nullable)     | Identificador de la categoría en la fuente.   |
| created_at    | datetime           | Fecha de alta.                                |
| updated_at    | datetime           | Última actualización.                         |

### `products`

Identidad "lógica" de un producto dentro de una fuente: lo que no cambia entre scrapes.

| Campo            | Tipo               | Descripción                                       |
|------------------|--------------------|-----------------------------------------------------|
| id               | int (PK)           | Identificador interno.                               |
| source_id        | int (FK)           | Fuente a la que pertenece.                           |
| category_id      | int (FK, nullable) | Categoría asociada.                                  |
| external_id      | str (nullable)     | Identificador del producto en la fuente, si existe.  |
| name             | str                | Nombre del producto (último conocido).               |
| brand            | str (nullable)     | Marca del producto, si se pudo extraer.              |
| normalized_name  | str (nullable)     | Nombre normalizado (lowercase, espacios colapsados). |
| product_url      | str                | URL del producto.                                    |
| image_url        | str (nullable)     | URL de imagen (última conocida).                     |
| created_at       | datetime           | Primera vez que se vio el producto.                  |
| updated_at       | datetime           | Última actualización.                                |

Restricción única sobre `(source_id, product_url)`: evita duplicar el mismo producto de la misma
fuente en corridas sucesivas (ver `get_or_create_product` en el repositorio).

### `product_snapshots`

Estado del producto en un momento dado (un registro por cada vez que se scrapea con éxito).

| Campo                | Tipo               | Descripción                                  |
|----------------------|--------------------|-------------------------------------------------|
| id                   | int (PK)           | Identificador interno.                          |
| product_id           | int (FK)           | Producto al que pertenece el snapshot.          |
| scraped_at           | datetime           | Momento en que se capturó el snapshot.          |
| price                | decimal            | Precio en el momento del snapshot.              |
| list_price           | decimal (nullable) | Precio de lista, si hay descuento.              |
| discount_percentage  | decimal (nullable) | Porcentaje de descuento, si aplica.             |
| currency             | str                | Moneda (ej. "ARS", "USD").                      |
| available            | bool               | Si el producto estaba disponible.               |
| raw_hash             | str (nullable)     | Hash del contenido crudo, para detectar cambios.|

Índice compuesto sobre `(product_id, scraped_at)` para las consultas históricas más comunes
("evolución de precio de un producto").

### `scrape_runs`

Una ejecución del scraper sobre una fuente.

| Campo               | Tipo               | Descripción                                  |
|---------------------|--------------------|--------------------------------------------------|
| id                  | int (PK)           | Identificador interno.                            |
| source_id           | int (FK)           | Fuente scrapeada.                                 |
| started_at          | datetime           | Inicio de la corrida.                             |
| finished_at         | datetime (nullable)| Fin de la corrida.                                |
| status              | str                | "running", "success", "partial", "failed".        |
| products_found      | int                | Productos encontrados en la corrida.              |
| products_inserted   | int                | Productos nuevos insertados.                      |
| products_updated    | int                | Productos ya existentes actualizados.             |
| errors_count        | int                | Cantidad de errores registrados.                  |
| created_at          | datetime           | Fecha de alta del registro.                       |

### `scrape_errors`

Errores de extracción ocurridos durante una corrida.

| Campo        | Tipo            | Descripción                                    |
|--------------|-----------------|---------------------------------------------------|
| id           | int (PK)        | Identificador interno.                             |
| run_id       | int (FK)        | Corrida en la que ocurrió el error.                |
| url          | str (nullable)  | URL involucrada, si aplica.                        |
| error_type   | str             | Tipo de error (ej. "ParsingError", "HttpClientError").|
| message      | str             | Detalle del error.                                 |
| created_at   | datetime        | Momento en que se registró el error.               |

## Relaciones

```
sources 1---N categories
sources 1---N products
sources 1---N scrape_runs
categories 1---N products (opcional)
products 1---N product_snapshots
scrape_runs 1---N scrape_errors
```

## `Product` vs `ProductSnapshot`

`Product` (tabla `products`) es el catálogo: identifica de forma estable "este producto de esta
fuente", y solo guarda los atributos que tiene sentido tratar como "último valor conocido" (nombre,
marca, imagen). `ProductSnapshot` (tabla `product_snapshots`) es el histórico: un registro nuevo
por cada scrape exitoso, con el precio y la disponibilidad de ese momento. Separarlos permite
responder preguntas como "¿qué productos cambiaron de precio esta semana?" sin sobrescribir datos
anteriores ni duplicar el catálogo en cada corrida.

Nótese que esta capa de persistencia (SQLAlchemy) es independiente del modelo de validación
Pydantic (`models/product.py`, usado para validar lo que devuelve el parser). Uno es el esquema de
base de datos; el otro, el contrato de datos scrapeados antes de guardarlos.

## Por qué guardar histórico

El objetivo de negocio del proyecto (`docs/05_business_questions.md`) incluye analizar evolución de
precios y disponibilidad en el tiempo. Si cada scrape sobrescribiera el mismo registro de producto,
se perdería esa información. Guardar un `ProductSnapshot` por corrida permite reconstruir la serie
de tiempo completa de cualquier producto.

## Por qué SQLite alcanza para esta etapa

Ver `docs/adr/0003-use-sqlite-first.md`. En resumen: el proyecto corre localmente y en GitHub
Actions, sin usuarios concurrentes reales ni infraestructura de base de datos propia. SQLite no
requiere instalar ni levantar un servidor, y SQLAlchemy aísla el resto del código de esa decisión:
migrar a PostgreSQL más adelante implicaría cambiar la URL de conexión, no el modelo ni el
repositorio.

## Qué queda para una etapa futura

- **Migraciones (Alembic)**: por ahora el esquema se crea con `Base.metadata.create_all` (ver
  `init_db` en `models/database.py`), sin versionado de cambios de esquema. Si el modelo empieza a
  cambiar con frecuencia entre etapas, agregar Alembic amerita su propia spec/ADR.
- **Motor de base de datos productivo** (PostgreSQL u otro): fuera de alcance mientras el proyecto
  sea de portfolio/laboratorio.
- **Deduplicación e identidad de producto más sofisticada** (por `external_id`, variantes,
  matching entre fuentes): el modelo actual dedupe por `(source_id, product_url)`, que alcanza
  para una única fuente demo.

## Cómo se usa (resumen)

```bash
python -m retail_scraping_lab.cli init-db               # crea las tablas si no existen
python -m retail_scraping_lab.cli scrape-demo            # corre el demo, exporta JSON (sin DB)
python -m retail_scraping_lab.cli scrape-demo --persist  # corre el demo y además guarda en DB
```

`repositories/product_repository.py` expone las operaciones de escritura (`get_or_create_source`,
`get_or_create_product`, `create_product_snapshot`, `create_scrape_run`, `finish_scrape_run`,
`create_scrape_error`, `save_scraped_products`); `services/scraping_service.py` las orquesta cuando
se corre con `--persist`.
