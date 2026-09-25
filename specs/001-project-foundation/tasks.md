# Tasks 001: Project Foundation

- [x] Crear estructura de carpetas completa (`src/`, `dashboard/`, `data/`, `tests/`, `docs/`,
      `specs/`, `.github/workflows/`) con `__init__.py` y `.gitkeep` donde corresponda.
- [x] Crear `pyproject.toml` con dependencias, configuración de `ruff`, `mypy` y `pytest`.
- [x] Crear `.gitignore`.
- [x] Crear `.env.example`.
- [x] Crear `Makefile` con los comandos `install`, `lint`, `format`, `typecheck`, `test`,
      `run-demo`, `dashboard`.
- [x] Crear `CLAUDE.md` y `AGENTS.md`.
- [x] Crear `docs/00_project_vision.md` a `docs/06_ai_agents_usage.md`.
- [x] Crear `docs/adr/0001` a `docs/adr/0005`.
- [x] Crear `config/settings.py` (Pydantic Settings) y `core/logging.py`, `core/exceptions.py`.
- [x] Crear skeleton de `scraping/clients/http_client.py`.
- [x] Crear skeleton de `scraping/parsers/product_parser.py`.
- [x] Crear skeleton de `scraping/spiders/demo_store_spider.py`.
- [x] Crear skeleton de `scraping/pipelines/product_pipeline.py`.
- [x] Crear skeleton de `models/product.py` y `models/database.py`.
- [x] Crear skeleton de `repositories/product_repository.py`.
- [x] Crear skeleton de `services/scraping_service.py`.
- [x] Crear skeleton de `analytics/queries.py`.
- [x] Crear `cli.py` con comando `scrape-demo` (Typer).
- [x] Crear `dashboard/app.py` y `dashboard/README.md`.
- [x] Crear fixture `tests/fixtures/demo_product_page.html`.
- [x] Crear `tests/unit/test_product_parser.py`.
- [x] Crear `tests/integration/test_scraping_pipeline.py`.
- [x] Crear `.github/workflows/ci.yml` y `.github/workflows/scrape.yml`.
- [x] Crear `README.md` orientado a portfolio.
- [x] Crear carpetas `specs/002-product-scraper` a `specs/005-dashboard` con `spec.md`, `plan.md`
      y `tasks.md`.
- [x] Validar localmente: `pip install -e ".[dev]"`, `make lint`, `make typecheck`, `make test`.
- [x] Inicializar el repositorio Git y hacer el primer commit (fuera del alcance de esta
      inicialización automática; a cargo del desarrollador).
