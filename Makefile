.PHONY: install lint format typecheck test run-demo dashboard

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
	python -m retail_scraping_lab.cli

dashboard:
	streamlit run dashboard/app.py
