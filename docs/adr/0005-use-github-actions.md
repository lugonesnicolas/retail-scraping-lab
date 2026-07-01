# ADR 0005: Usar GitHub Actions para CI y ejecución manual del scraper demo

## Estado

Aceptado.

## Contexto

El proyecto es un repositorio público en GitHub, pensado como portfolio. Se necesita (1) validar
automáticamente la calidad del código (lint, typecheck, tests) en cada cambio, y (2) demostrar
que el scraper demo se puede ejecutar de forma reproducible fuera del entorno local del
desarrollador.

## Decisión

Se usa GitHub Actions con dos workflows:

- `ci.yml`: se ejecuta en cada push/PR, instala dependencias y corre `ruff`, `mypy` y `pytest`.
- `scrape.yml`: workflow manual (`workflow_dispatch`) que ejecuta el scraper demo contra el
  fixture local y sube los artefactos generados (JSON/CSV) como resultado de la ejecución.

## Alternativas consideradas

- **Otro proveedor de CI (GitLab CI, CircleCI, Jenkins)**: requeriría infraestructura o cuentas
  adicionales; GitHub Actions está integrado de forma nativa en GitHub, donde vive el
  repositorio, y es gratuito para repositorios públicos.
- **No tener CI**: más simple a corto plazo, pero no demuestra una práctica profesional
  relevante (integración continua) que el proyecto busca mostrar como parte del portfolio.

## Consecuencias

- Cualquier visitante del repositorio puede ver, desde el badge de estado o la pestaña
  "Actions", que el código pasa lint, typecheck y tests de forma automática.
- El workflow `scrape.yml` sirve como demostración tangible de que el scraper demo funciona de
  forma reproducible, sin depender del entorno local del desarrollador.
- A futuro, `scrape.yml` podría extenderse para correr contra fuentes reales de forma programada
  (`schedule`), lo cual se evaluará y documentará cuando el proyecto llegue a esa etapa,
  respetando siempre las restricciones éticas descritas en `README.md` y `AGENTS.md`.
