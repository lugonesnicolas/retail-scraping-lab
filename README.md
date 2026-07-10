# retail-scraping-lab

Laboratorio educativo y profesional de **scraping aplicado a inteligencia de productos y
precios** en retail, construido con Python avanzado, SQL, modelado de datos, GitHub Actions y un
dashboard de análisis, siguiendo un flujo de **Spec-Driven Development (SDD)**.

## Propósito

Este proyecto es parte de mi portfolio como desarrollador Python / Data Engineer en formación
(Tecnicatura en Desarrollo de Software). Su objetivo es demostrar, de forma concreta y
verificable, capacidad de:

- Diseñar una arquitectura de software clara y mantenible.
- Modelar datos pensando en preguntas de negocio, no solo en "guardar lo que se scrapea".
- Escribir SQL y usar un ORM (SQLAlchemy) de forma criteriosa.
- Configurar integración continua y un flujo de trabajo profesional.
- Usar agentes de IA (ChatGPT, Claude Code, Codex, Gemini Pro) como aceleradores de desarrollo,
  de forma documentada y crítica, no como caja negra.

## Qué problema intenta resolver

Simula, a pequeña escala, el tipo de sistema que un equipo de retail/e-commerce usaría para
monitorear precios y disponibilidad de productos: obtener datos de una fuente, validarlos,
persistirlos de forma histórica y analizarlos para responder preguntas de negocio (ver
`docs/05_business_questions.md`).

## Por qué esto no es "solo un scraper"

El scraper en sí es intencionalmente simple. El valor del proyecto está en todo lo que lo rodea:
una arquitectura en capas explícita, un modelo de datos pensado para análisis histórico, tests
automatizados, CI/CD, un dashboard de análisis, y un proceso de trabajo documentado (SDD) que
permite explicar, paso a paso, por qué el proyecto está construido como está.

## Stack

- Python 3.12+
- `requests` — cliente HTTP
- `lxml` — parsing HTML/XML con XPath
- `pydantic` / `pydantic-settings` — validación de datos y configuración
- `sqlalchemy` — modelado de datos y persistencia (SQLite en esta etapa)
- `typer` + `rich` — CLI
- `streamlit` + `pandas` — dashboard de análisis
- `pytest`, `ruff`, `mypy` — testing, lint/format y chequeo de tipos

> **Nota**: el proyecto arranca con `requests` + `lxml` de forma deliberada (no `httpx`, no
> `beautifulsoup4`). La justificación completa está en
> [`docs/adr/0002-use-requests-and-lxml.md`](docs/adr/0002-use-requests-and-lxml.md).

## Arquitectura (resumen)

```
cliente HTTP (requests) -> parser (lxml/XPath) -> validación (Pydantic)
    -> pipeline (export JSON/CSV) -> repositorio (SQLAlchemy) -> analytics/dashboard
```

Cada capa tiene una responsabilidad única y es testeable de forma aislada. El detalle completo
está en [`docs/02_architecture.md`](docs/02_architecture.md).

## Instalación

Requiere Python 3.12 o superior.

```bash
python -m venv .venv
source .venv/bin/activate
make install
```

Copiar `.env.example` a `.env` y ajustar las variables si hace falta:

```bash
cp .env.example .env
```

## Cómo correr los tests

```bash
make test
```

Los tests no dependen de acceso a internet: usan el fixture local
`tests/fixtures/demo_product_page.html`.

También se puede lintear y chequear tipos:

```bash
make lint
make typecheck
```

## Cómo correr la demo

```bash
make run-demo
```

Esto ejecuta el spider demo sobre el fixture local, valida los productos extraídos con Pydantic
y exporta el resultado a `data/exports/`.

## Cómo persistir en base de datos

```bash
make init-db                                              # crea las tablas si no existen
python -m retail_scraping_lab.cli scrape-demo --persist   # corre el demo y guarda en la DB
```

Esto guarda los productos scrapeados como `Product` (catálogo) y `ProductSnapshot` (histórico)
en una base SQLite local (`data/processed/retail_scraping_lab.db` por defecto). Ver
[`docs/03_data_model.md`](docs/03_data_model.md) para el detalle del modelo de datos.

## Cómo abrir el dashboard

```bash
make run-demo   # si todavía no generaste datos de ejemplo
make dashboard
```

El dashboard (Streamlit) lee el export más reciente de `data/exports/` y muestra cantidad de
productos, precio promedio, disponibilidad y una tabla de productos. Más detalle en
[`dashboard/README.md`](dashboard/README.md).

## Roadmap

El proyecto avanza por etapas, cada una documentada como una spec en `specs/` (ver
[`docs/01_sdd_process.md`](docs/01_sdd_process.md) para el proceso):

- [x] `001-project-foundation` — estructura base del repositorio.
- [x] `002-product-scraper` — cliente HTTP, parser, validación y pipeline de export.
- [x] `003-data-model` — persistencia completa con SQLAlchemy.
- [ ] `004-github-actions` — CI y workflow manual de scraping demo.
- [ ] `005-dashboard` — dashboard de análisis en Streamlit.

## Aviso ético sobre scraping

- No se scrapea LinkedIn bajo ninguna circunstancia.
- No se automatizan publicaciones ni comentarios en ninguna red social.
- El scraping se realiza sobre fixtures locales o fuentes públicas/de prueba, con bajo volumen,
  respetando `robots.txt` cuando aplica y sin extraer datos sensibles o personales.
- El detalle completo de la estrategia de scraping está en
  [`docs/04_scraping_strategy.md`](docs/04_scraping_strategy.md).

## Estado actual del proyecto

Estructura, documentación, specs, scraping demo (cliente, parser, pipeline) y persistencia
histórica completa con SQLAlchemy (`003-data-model`) funcionando sobre datos de ejemplo. El CI
completo y el dashboard de análisis histórico son el foco de las próximas etapas.

## Documentación y proceso de trabajo

- [`docs/00_project_vision.md`](docs/00_project_vision.md) — visión y alcance del proyecto.
- [`docs/01_sdd_process.md`](docs/01_sdd_process.md) — proceso de Spec-Driven Development.
- [`docs/02_architecture.md`](docs/02_architecture.md) — arquitectura en capas.
- [`docs/03_data_model.md`](docs/03_data_model.md) — modelo de datos objetivo.
- [`docs/04_scraping_strategy.md`](docs/04_scraping_strategy.md) — estrategia de scraping.
- [`docs/05_business_questions.md`](docs/05_business_questions.md) — preguntas de negocio.
- [`docs/06_ai_agents_usage.md`](docs/06_ai_agents_usage.md) — uso de agentes de IA.
- [`docs/adr/`](docs/adr/) — decisiones de arquitectura registradas.
- [`CLAUDE.md`](CLAUDE.md) / [`AGENTS.md`](AGENTS.md) — reglas para agentes de IA que
  colaboran en este repositorio.
