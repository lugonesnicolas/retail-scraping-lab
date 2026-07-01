# Modelo de datos

Este documento propone el modelo de datos objetivo del proyecto. La implementación inicial en
`src/retail_scraping_lab/models/database.py` es una base (skeleton); el modelo completo se irá
construyendo en la spec `003-data-model` (ver `specs/003-data-model/`).

El diseño separa el "catálogo" (qué producto es) de los "snapshots" (cómo estaba ese producto en
un momento dado), para poder responder preguntas históricas como "cómo evolucionó el precio de
este producto" sin perder información en cada scrape.

## Entidades

### `source`

Representa una fuente de datos (un sitio o fixture de donde se obtienen productos).

| Campo        | Tipo      | Descripción                                  |
|--------------|-----------|-----------------------------------------------|
| id           | int (PK)  | Identificador interno.                        |
| name         | str       | Nombre de la fuente (ej. "demo-store").        |
| base_url     | str       | URL base o identificador de la fuente.         |
| is_active    | bool      | Si la fuente está habilitada para scrapear.    |
| created_at   | datetime  | Fecha de alta.                                 |

### `category`

Categoría de producto, propia del dominio del proyecto (no necesariamente igual a la de la
fuente original).

| Campo        | Tipo      | Descripción                                  |
|--------------|-----------|-----------------------------------------------|
| id           | int (PK)  | Identificador interno.                        |
| name         | str       | Nombre de la categoría.                        |
| parent_id    | int (FK, nullable) | Categoría padre, para jerarquías simples. |

### `product`

Identidad "lógica" de un producto dentro de una fuente: lo que no cambia entre scrapes.

| Campo          | Tipo      | Descripción                                       |
|----------------|-----------|-----------------------------------------------------|
| id             | int (PK)  | Identificador interno.                               |
| source_id      | int (FK)  | Fuente a la que pertenece.                           |
| category_id    | int (FK, nullable) | Categoría asociada.                         |
| external_id    | str       | Identificador del producto en la fuente (si existe). |
| name           | str       | Nombre del producto (último conocido).               |
| product_url    | str       | URL del producto.                                    |
| image_url      | str (nullable) | URL de imagen (última conocida).                |
| created_at     | datetime  | Primera vez que se vio el producto.                  |

### `product_snapshot`

Estado del producto en un momento dado (un registro por cada vez que se scrapea con éxito).

| Campo          | Tipo      | Descripción                                       |
|----------------|-----------|-----------------------------------------------------|
| id             | int (PK)  | Identificador interno.                               |
| product_id     | int (FK)  | Producto al que pertenece el snapshot.               |
| scrape_run_id  | int (FK)  | Corrida de scraping que generó este snapshot.        |
| price          | decimal   | Precio en el momento del snapshot.                   |
| currency       | str       | Moneda (ej. "ARS", "USD").                           |
| availability   | str       | Disponibilidad (ej. "in_stock", "out_of_stock").     |
| captured_at    | datetime  | Momento en que se capturó el snapshot.               |

### `scrape_run`

Una ejecución del scraper sobre una fuente.

| Campo          | Tipo      | Descripción                                       |
|----------------|-----------|-----------------------------------------------------|
| id             | int (PK)  | Identificador interno.                               |
| source_id      | int (FK)  | Fuente scrapeada.                                    |
| started_at     | datetime  | Inicio de la corrida.                                |
| finished_at    | datetime (nullable) | Fin de la corrida.                          |
| status         | str       | "success", "partial", "failed".                      |
| items_scraped  | int       | Cantidad de productos scrapeados con éxito.           |

### `scrape_error`

Errores de extracción ocurridos durante una corrida, asociados o no a un producto específico.

| Campo          | Tipo      | Descripción                                       |
|----------------|-----------|-----------------------------------------------------|
| id             | int (PK)  | Identificador interno.                               |
| scrape_run_id  | int (FK)  | Corrida en la que ocurrió el error.                  |
| product_url    | str (nullable) | URL involucrada, si aplica.                     |
| error_type     | str       | Tipo de error (ej. "parse_error", "http_error").      |
| message        | str       | Detalle del error.                                    |
| occurred_at    | datetime  | Momento del error.                                    |

## Relaciones

```
source 1---N product
source 1---N scrape_run
category 1---N product (opcional)
product 1---N product_snapshot
scrape_run 1---N product_snapshot
scrape_run 1---N scrape_error
```

## Notas de diseño

- Separar `product` de `product_snapshot` permite responder "qué productos cambiaron de precio"
  y "cómo evolucionan los precios en el tiempo" (ver `docs/05_business_questions.md`) sin
  sobrescribir información histórica.
- `scrape_run` y `scrape_error` permiten auditar cada corrida y detectar productos con errores de
  extracción de forma sistemática, en vez de solo loguearlos.
- Este modelo es intencionalmente simple (sin variantes de producto, sin multi-idioma, etc.) para
  mantener el foco educativo del proyecto. Extensiones futuras deberían proponerse como una spec
  nueva.
