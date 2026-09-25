# retail-scraping-lab

[![CI](https://github.com/lugonesnicolas/retail-scraping-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/lugonesnicolas/retail-scraping-lab/actions/workflows/ci.yml)

Pipeline end-to-end para **monitorear productos, precios y disponibilidad en retail**: adquiere
datos de una fuente, los parsea, normaliza y valida, los guarda como histórico en SQL y los
expone en un dashboard de análisis. Escrito en Python con `requests`, `lxml`, Pydantic,
SQLAlchemy y Streamlit.

```
Retail source → Acquisition → Parsing → Normalization → Validation → Historical storage → Analytics / Dashboard
```

> **Estado: `v0.1.0`.** Es un vertical slice completo sobre una fuente demo local y
> reproducible. No es un sistema productivo; ver [Estado del proyecto](#estado-del-proyecto).

---

## Problema

Una empresa de retail necesita monitorear periódicamente productos de fuentes externas (su propio
catálogo o el de competidores) para responder preguntas como:

- ¿Cuál es el precio actual de cada producto?
- ¿Cómo cambió respecto de la observación anterior?
- ¿Qué productos están disponibles?
- ¿Cuál es el precio promedio?
- ¿Cuándo se observó cada dato y de qué fuente proviene?

Un script que "scrapea y guarda un CSV" no alcanza para esto:

- cada corrida pisa la anterior y se pierde el histórico;
- un producto mal formado rompe toda la corrida;
- los formatos de la fuente (`"$ 45.999,90"`, `"Sin stock"`) terminan mezclados con los datos;
- nadie sabe qué corridas fallaron ni por qué.

## Solución

Un pipeline reproducible con capas separadas y un modelo de datos histórico:

1. **Acquisition**: obtiene el contenido crudo de la fuente.
2. **Parsing**: extrae los campos de cada producto como texto (XPath).
3. **Normalization**: convierte ese texto a valores del dominio (`Decimal`, enums).
4. **Validation**: valida cada producto contra un contrato Pydantic.
5. **Historical storage**: guarda una observación fechada por producto y captura en SQLite (vía
   SQLAlchemy). La carga es idempotente.
6. **Analytics / Dashboard**: consultas SQL de solo lectura y un dashboard Streamlit que las
   consume.

Cada corrida queda registrada con su estado (`success`, `partial`, `failed`) y sus errores. Un
producto inválido se descarta y se registra, sin detener el resto.

## Arquitectura

```
tests/fixtures/demo_store/<fecha>/catalog.html        fuente demo (una carpeta por captura)
        │
        ▼
scraping/clients      LocalFileClient | HttpClient   acquisition: contenido crudo
        │
        ▼
scraping/parsers      parse_catalog (lxml + XPath)   parsing: campos de texto por producto
        │
        ▼
scraping/normalizers  product_normalizer             normalization: "$ 45.999,90" → Decimal
        │
        ▼
models/product.py     Product (Pydantic)             validation: contrato de una observación
        │
        ├──▶ scraping/pipelines   export JSON/CSV por captura
        ▼
repositories          ProductRepository              persistencia histórica (SQLAlchemy)
        │
        ▼
analytics/queries.py  consultas de solo lectura  ──▶  dashboard/app.py (Streamlit)
```

- `services/scraping_service.py` orquesta el caso de uso: una captura, un run.
- `cli.py` lo expone por línea de comandos (Typer).

La regla central es que **cada capa hace una sola cosa**:

- el cliente no sabe de HTML;
- el parser no convierte tipos;
- el normalizador no hace I/O;
- el dashboard no tiene SQL ni lógica de negocio: solo llama a `analytics/queries.py`.

Cambiar la fuente implica escribir otro cliente, parser y normalizador. El modelo, la
persistencia y el dashboard no cambian. Detalle en
[`docs/02_architecture.md`](docs/02_architecture.md).

## Modelo de datos

El diseño separa **qué producto es** de **cómo estaba en un momento dado**:

```
sources 1──N products 1──N product_snapshots
sources 1──N scrape_runs 1──N scrape_errors
```

- **`products`** es el catálogo: identidad estable del producto dentro de una fuente, única por
  `(source_id, product_url)`, con el último nombre, marca e imagen observados.
- **`product_snapshots`** es el histórico: una fila por producto y por captura, con precio, moneda
  y disponibilidad. Una restricción única `(product_id, scraped_at)` hace idempotente la carga.
- **`scrape_runs`** y **`scrape_errors`** son la trazabilidad operativa de cada ejecución.

Correspondencia entre el registro normalizado de una observación y el modelo:

| Campo del registro | Pydantic (`models/product.py`) | Persistencia                         |
|--------------------|--------------------------------|--------------------------------------|
| source             | `source`                       | `sources.name`                       |
| source_url         | `product_url`                  | `products.product_url`               |
| product_name       | `name`                         | `products.name`                      |
| brand              | `brand`                        | `products.brand`                     |
| price              | `price` (`Decimal`, ≥ 0)       | `product_snapshots.price`            |
| currency           | `currency` (ISO, 3 letras)     | `product_snapshots.currency`         |
| availability       | `availability` (enum)          | `product_snapshots.availability`     |
| captured_at        | `captured_at`                  | `product_snapshots.scraped_at`       |

Detalle completo en [`docs/03_data_model.md`](docs/03_data_model.md).

## Decisiones de ingeniería

- **Scraper propio con `requests` + `lxml`, sin framework.** El objetivo es que cada etapa sea
  explícita y testeable por separado, no maximizar el throughput.
  [ADR 0001](docs/adr/0001-use-python-custom-scraper.md) ·
  [ADR 0002](docs/adr/0002-use-requests-and-lxml.md)
- **Acquisition como contrato (`ContentClient`).** `LocalFileClient` y `HttpClient` cumplen la
  misma interfaz, y el spider recibe el cliente inyectado. Por eso la demo corre offline sin
  atajos en el código.
- **Normalizar antes de validar.** El parser entrega texto crudo; el normalizador aplica el
  formato de la fuente (precios `es-AR`, textos de stock); Pydantic valida el contrato final.
  Ninguna capa conoce detalles de la otra.
- **Errores por ítem, no por página.** Un producto inválido se registra como `scrape_error` y el
  run queda `partial`. Solo falla la captura completa si no se puede leer o si su estructura
  cambió.
- **`captured_at` es cuándo se observó el dato, no cuándo se cargó.** El momento de ejecución
  queda aparte, en `scrape_runs.started_at`.
- **Carga idempotente garantizada por la base.** La restricción única `(product_id, scraped_at)`
  permite reprocesar una captura sin duplicar historia; los omitidos se cuentan en el run.
- **Disponibilidad como enum de tres estados.** Guardar un booleano convertiría "desconocida" en
  "sin stock".
- **Transacciones separadas por run.** El run se crea antes de guardar los datos, así que una
  falla al persistir queda registrada como `failed` con su error en lugar de perderse en el
  rollback.
- **SQLite + SQLAlchemy.** Cero infraestructura para quien clona el repo; pasar a PostgreSQL es
  cambiar la URL. [ADR 0003](docs/adr/0003-use-sqlite-first.md)
- **Streamlit sobre una capa de analytics.** Las consultas (incluida una window function para
  la variación de precio) son funciones testeadas que devuelven dataclasses.
  [ADR 0004](docs/adr/0004-use-streamlit-dashboard.md)

Cada feature se construyó con Spec-Driven Development: `specs/NNN-feature/` contiene `spec.md`,
`plan.md` y `tasks.md`. Ver [`docs/01_sdd_process.md`](docs/01_sdd_process.md).

## Cómo correrlo localmente

Requisitos: Python 3.12+, `git` y `make`.

```bash
git clone https://github.com/lugonesnicolas/retail-scraping-lab.git
cd retail-scraping-lab
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
make install                     # instala el paquete y las herramientas de desarrollo
make run-demo                    # corre el pipeline completo y guarda el histórico
make dashboard                   # levanta el dashboard; abrir http://localhost:8501
```

Todos los comandos se corren desde la raíz del repositorio. La configuración tiene valores por
defecto y no requiere ningún archivo. Para cambiarla, copiar `.env.example` a `.env` (por
ejemplo, `RSL_DATABASE_URL` para usar otra base).

| `make`           | Equivalente sin `make`                                     | Qué hace                                  |
|------------------|------------------------------------------------------------|-------------------------------------------|
| `make install`   | `pip install -e ".[dev]"`                                  | Instala dependencias                      |
| `make run-demo`  | `python -m retail_scraping_lab.cli scrape-demo --persist`  | Pipeline completo + histórico en SQLite   |
| `make dashboard` | `streamlit run dashboard/app.py --server.headless true`    | Levanta el dashboard                      |
| `make check`     | `ruff check . && ruff format --check . && mypy && pytest`  | Lint, formato, tipos y tests              |
| `make reset-db`  | `python -m retail_scraping_lab.cli init-db --reset`        | Borra y recrea la base                    |

Otras opciones del CLI:

```bash
python -m retail_scraping_lab.cli scrape-demo --capture 2026-09-08 --persist   # una sola captura
python -m retail_scraping_lab.cli scrape-demo                                  # solo export, sin base
python -m retail_scraping_lab.cli --help
```

## Testing

```bash
make check
```

Corre `ruff` (lint y formato), `mypy` y la suite de `pytest`, **sin acceso a internet**. Los
tests cubren:

- **Unitarios**:
  - parser, sobre HTML local;
  - normalizador, con casos parametrizados de precio, disponibilidad y texto;
  - clientes: `HttpClient` con `requests` simulado vía `monkeypatch`;
  - repositorio, sobre SQLite en memoria;
  - consultas analíticas.
- **Integración**:
  - ingesta de las tres capturas con el histórico esperado;
  - idempotencia;
  - run `partial` con su error persistido;
  - regresión de la falla de persistencia;
  - captura ilegible;
  - CLI con `CliRunner`;
  - smoke test del dashboard con `streamlit.testing.AppTest`.

GitHub Actions corre las mismas validaciones en cada push a `main` y en cada PR
([`ci.yml`](.github/workflows/ci.yml)). Un segundo workflow manual
([`scrape.yml`](.github/workflows/scrape.yml)) corre el pipeline completo y publica los exports y
la base SQLite como artefactos.

## Demo

La fuente demo, `demo-store`, es un catálogo de artículos deportivos con tres capturas semanales
en [`tests/fixtures/demo_store/`](tests/fixtures/demo_store/). Las capturas incluyen a propósito
los casos que un pipeline real tiene que resolver:

- cambios de precio;
- un producto que se agota y vuelve;
- un producto nuevo;
- disponibilidad "Consultar disponibilidad" (desconocida);
- un producto sin marca;
- un precio `"Consultar precio"` que no se puede interpretar.

`make run-demo` produce:

```
                           Resumen por captura
┏━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Captura    ┃ Estado  ┃ Items ┃ Validos ┃ Errores ┃ Snapshots nuevos ┃ Snapshots omitidos ┃
┡━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 2026-09-01 │ success │    10 │      10 │       0 │               10 │                  0 │
│ 2026-09-08 │ partial │    10 │       9 │       1 │                9 │                  0 │
│ 2026-09-15 │ success │    11 │      11 │       0 │               11 │                  0 │
└────────────┴─────────┴───────┴─────────┴─────────┴──────────────────┴────────────────────┘
```

Queda un histórico de 11 productos y 30 observaciones. El producto inválido se registra como
`NormalizationError` con su URL. Correr `make run-demo` otra vez no agrega nada: todas las
observaciones aparecen como omitidas.

Cada captura también se exporta a `data/exports/demo-store_<fecha>.json`.

## Dashboard

`make dashboard` abre una aplicación Streamlit que lee la base SQLite a través de
`analytics/queries.py`:

| Pregunta de negocio                                 | Sección           | Consulta                          |
|-----------------------------------------------------|-------------------|-----------------------------------|
| ¿Cuántos productos y observaciones hay?             | Overview          | `count_products`, `count_snapshots` |
| ¿Cuál es el precio promedio actual?                 | Overview          | `average_current_price`           |
| ¿Qué productos están disponibles?                   | Overview / Latest | `current_availability_breakdown`  |
| ¿Cuál es el precio actual, de qué fuente y cuándo se observó? | Latest products | `latest_snapshots`          |
| ¿Cómo cambió respecto de la observación anterior?   | Price changes     | `price_changes` (window function) |
| ¿Cómo evolucionó el precio de un producto?          | Price history     | `price_history`                   |
| ¿Qué corridas hubo, cómo terminaron y qué falló?    | Scrape runs / Errors | `recent_scrape_runs`, `recent_errors` |

Con los datos de la demo, por ejemplo, "Price changes" muestra que las Zapatillas Trail X bajaron
de $62.500 a $58.999 (−5,6 %) y las Medias de Compresión subieron de $7.250 a $7.650 (+5,5 %).
Todas las fechas se muestran en UTC. Si la base todavía no existe, el dashboard muestra los
comandos para generarla. Más detalle en [`dashboard/README.md`](dashboard/README.md).

## Estado del proyecto

**`v0.1.0` cumple la Definition of Done:** se puede clonar el repositorio, correr el pipeline
completo, acumular snapshots históricos, correr los tests y ver los resultados en el dashboard
siguiendo solo este README.

Lo que deliberadamente **no** es, todavía:

- **No scrapea un sitio real.** La fuente es un catálogo local con capturas fechadas.
  `HttpClient` existe y está testeado, pero ningún spider en vivo lo usa aún.
- **No es productivo.** No hay scheduling, alertas, autenticación, migraciones de esquema
  (Alembic) ni una base de datos servidor.
- **Una sola fuente y una sola moneda.** El precio promedio no convierte monedas.

### Roadmap (v0.2+)

- Una fuente HTTP real pensada para practicar scraping, con `robots.txt`, rate limiting y
  reintentos.
- Migraciones con Alembic y soporte de PostgreSQL.
- Ejecución programada en GitHub Actions.
- Análisis por categoría, variación entre capturas arbitrarias y errores recurrentes (ver
  [`docs/05_business_questions.md`](docs/05_business_questions.md)).

## Alcance ético

- Scraping de bajo volumen, solo sobre fixtures locales o fuentes públicas pensadas para
  practicar, respetando `robots.txt` y los términos de uso cuando el objetivo sea un sitio real.
- No se extraen datos personales.
- No se scrapea LinkedIn ni se automatizan publicaciones en redes sociales.

Detalle en [`docs/04_scraping_strategy.md`](docs/04_scraping_strategy.md).

## Estructura del repositorio

```
src/retail_scraping_lab/
  scraping/        clients · parsers · normalizers · spiders · pipelines
  models/          contrato Pydantic y esquema SQLAlchemy
  repositories/    escritura en la base
  services/        orquestación del caso de uso (un run por captura)
  analytics/       consultas de solo lectura
  cli.py           comandos Typer
dashboard/         aplicación Streamlit
tests/             unit · integration · fixtures (catálogo demo)
docs/              visión, arquitectura, modelo de datos, estrategia, ADRs
specs/             una carpeta por feature (spec, plan, tasks)
```

## Documentación

- [`docs/00_project_vision.md`](docs/00_project_vision.md): visión y alcance.
- [`docs/01_sdd_process.md`](docs/01_sdd_process.md): proceso de Spec-Driven Development.
- [`docs/02_architecture.md`](docs/02_architecture.md): arquitectura en capas.
- [`docs/03_data_model.md`](docs/03_data_model.md): modelo de datos.
- [`docs/04_scraping_strategy.md`](docs/04_scraping_strategy.md): estrategia de scraping.
- [`docs/05_business_questions.md`](docs/05_business_questions.md): preguntas de negocio.
- [`docs/06_ai_agents_usage.md`](docs/06_ai_agents_usage.md): uso de agentes de IA en el
  desarrollo.
- [`docs/adr/`](docs/adr/): decisiones de arquitectura.
- [`CHANGELOG.md`](CHANGELOG.md): historial de versiones.
