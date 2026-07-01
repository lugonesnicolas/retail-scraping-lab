# Spec 001: Project Foundation

## Objetivo funcional

Inicializar `retail-scraping-lab` con una estructura de repositorio completa, profesional y
lista para evolucionar por etapas, de forma que cualquier desarrollador (humano o agente de IA)
pueda entender el propósito del proyecto, instalar el entorno, correr los comandos básicos y
saber dónde agregar código nuevo sin tener que inferir la arquitectura desde cero.

Esta es la spec fundacional del proyecto: no agrega funcionalidad de negocio (scraping real,
persistencia completa, análisis), sino la base sobre la que se construyen las specs siguientes
(`002-product-scraper`, `003-data-model`, `004-github-actions`, `005-dashboard`).

## Criterios de aceptación

- Existe una estructura de carpetas completa según lo descrito en `docs/02_architecture.md`:
  `src/retail_scraping_lab/` con sus subpaquetes, `dashboard/`, `data/`, `tests/`, `docs/`,
  `specs/`, `.github/workflows/`.
- `pyproject.toml` define el proyecto con Python 3.12+, el stack de dependencias obligatorio
  (`requests`, `lxml`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `typer`, `rich`,
  `streamlit`, `pandas`) y las herramientas de desarrollo (`pytest`, `ruff`, `mypy`), sin incluir
  `httpx` ni `beautifulsoup4`.
- `pip install -e ".[dev]"` instala el proyecto y sus dependencias sin errores en un entorno con
  Python 3.12+.
- `make lint`, `make format`, `make typecheck` y `make test` se ejecutan sin errores de
  configuración (pueden no reportar hallazgos si no hay código de negocio todavía, pero deben
  correr).
- Existe documentación base en `docs/` (visión, proceso SDD, arquitectura, modelo de datos,
  estrategia de scraping, preguntas de negocio, uso de agentes de IA) y ADRs iniciales en
  `docs/adr/`.
- Existen `CLAUDE.md` y `AGENTS.md` con reglas específicas para agentes de IA.
- Existe un `README.md` orientado a portfolio, en español, con nombres técnicos en inglés, que
  cubre instalación, tests, demo, dashboard, roadmap y aviso ético.
- Existen las carpetas de specs para las features siguientes (`002` a `005`), cada una con
  `spec.md`, `plan.md` y `tasks.md`.
- El código fuente inicial (`src/retail_scraping_lab/`) compila/importa sin errores de sintaxis,
  aunque su lógica de negocio sea todavía un skeleton (placeholders documentados).
- `.gitignore` excluye artefactos de entorno, cachés de herramientas y datos generados en
  `data/`, sin excluir la estructura de carpetas (`.gitkeep`).
- `.env.example` documenta las variables de configuración esperadas por `config/settings.py`.

## Fuera de alcance de esta spec

- Implementación completa del parser, pipeline o repositorio (se skeletoniza, se completa en
  `002-product-scraper` y `003-data-model`).
- Workflows de GitHub Actions completos y probados en CI real (se define su forma básica aquí y
  se profundiza en `004-github-actions`).
- Dashboard con lógica de análisis completa (se skeletoniza, se completa en `005-dashboard`).
