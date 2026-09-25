.PHONY: install lint format typecheck test check run-demo init-db reset-db dashboard

install:
	pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy

test:
	pytest

check: lint typecheck test

# Ingiere todas las capturas del catalogo demo y guarda el historico en SQLite.
# Es idempotente: correrlo de nuevo no duplica snapshots.
run-demo:
	python -m retail_scraping_lab.cli scrape-demo --persist

init-db:
	python -m retail_scraping_lab.cli init-db

# Borra y recrea el esquema (necesario tras un cambio de modelo; no hay migraciones).
reset-db:
	python -m retail_scraping_lab.cli init-db --reset

dashboard:
	streamlit run dashboard/app.py
