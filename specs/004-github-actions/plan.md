# Plan 004: GitHub Actions

## Enfoque técnico

- `ci.yml`: job único `test` sobre `ubuntu-latest`, con `actions/setup-python` fijando
  `python-version: "3.12"`, `pip install -e ".[dev]"`, y pasos separados para `ruff check .`,
  `mypy` y `pytest`.
- `scrape.yml`: job único `run-demo` sobre `ubuntu-latest`, disparado solo por
  `workflow_dispatch`, que instala el proyecto, corre `make run-demo` y usa
  `actions/upload-artifact` para subir `data/exports/`.
- Ambos workflows viven en `.github/workflows/` y se mantienen simples, sin matrices de
  versiones (no es necesario para el alcance actual del proyecto).
