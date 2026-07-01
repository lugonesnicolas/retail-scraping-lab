# Spec 004: GitHub Actions

## Objetivo funcional

Configurar integración continua básica y un workflow manual para ejecutar el scraper demo desde
GitHub Actions, demostrando que el proyecto es reproducible fuera del entorno local. Ver
`docs/adr/0005-use-github-actions.md`.

## Criterios de aceptación

- `ci.yml` se dispara en `push` y `pull_request`, instala el proyecto (`pip install -e ".[dev]"`)
  y corre `ruff check`, `mypy` y `pytest` en ese orden, fallando el job si alguno falla.
- `scrape.yml` se dispara manualmente (`workflow_dispatch`), instala el proyecto, ejecuta el
  scraper demo (`make run-demo`) y sube el contenido de `data/exports/` como artefacto del run.
- Ambos workflows usan una versión de Python 3.12+ fijada explícitamente.

## Fuera de alcance de esta spec

- Ejecución programada (`schedule`) del scraper contra fuentes reales.
- Despliegue del dashboard como parte de CI/CD.
- Publicación de reportes de cobertura de tests (puede agregarse en una iteración futura).
