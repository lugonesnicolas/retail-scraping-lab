.PHONY: install lint format typecheck test run-demo init-db dashboard

install:
	pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy

test:
	pytest

run-demo:
	python -m retail_scraping_lab.cli scrape-demo

init-db:
	python -m retail_scraping_lab.cli init-db

dashboard:
	streamlit run dashboard/app.py
