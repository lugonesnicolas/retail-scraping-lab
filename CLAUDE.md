# Instrucciones para Claude Code

Este archivo contiene reglas específicas para Claude Code al trabajar en `retail-scraping-lab`.
Las reglas generales para cualquier agente de IA están en [AGENTS.md](AGENTS.md); léelo también.

## Contexto del proyecto

`retail-scraping-lab` es un laboratorio educativo y de portfolio, no un producto comercial.
El objetivo es que el código sea claro, testeable y fácil de explicar en una entrevista o en un
post de LinkedIn, no que resuelva el máximo de casos posibles. Ver `docs/00_project_vision.md`.

## Reglas de arquitectura

- Respetar la separación de capas descrita en `docs/02_architecture.md`: cliente HTTP → parser →
  validación (Pydantic) → pipeline → repositorio → analytics/dashboard. No mezclar
  responsabilidades entre capas (por ejemplo, no parsear HTML dentro del cliente HTTP).
- Usar `requests` para todas las peticiones HTTP. No agregar `httpx`.
- Usar `lxml` para todo el parsing de HTML/XML. No agregar `beautifulsoup4`.
- No agregar dependencias nuevas sin justificarlas explícitamente (en el mensaje de commit/PR o
  en un ADR si el cambio es estructural). El stack actual está definido en `pyproject.toml` y en
  `docs/adr/0002-use-requests-and-lxml.md`.

## Reglas de trabajo

- No crear archivos innecesarios. Cada archivo nuevo debe tener un propósito claro dentro de la
  estructura existente.
- No resolver una feature completa en un solo script o función gigante. Dividir en funciones y
  módulos pequeños, siguiendo la estructura de carpetas ya definida en `src/retail_scraping_lab/`.
- Antes de implementar una feature, revisar la spec correspondiente en `specs/<feature>/spec.md`
  y su `plan.md`. Si la tarea no tiene spec, proponer una antes de escribir código no trivial.
- Priorizar código simple, explícito y testeable por sobre abstracciones prematuras.
- Actualizar la documentación relevante (`docs/`, ADRs) cuando un cambio modifique la
  arquitectura, el modelo de datos o el stack.
- Generar tests para toda lógica nueva no trivial (parsers, pipelines, servicios). Los tests no
  deben depender de acceso a internet; usar fixtures locales en `tests/fixtures/`.
- Mantener el foco educativo y de portfolio: preferir código legible y bien comentado donde el
  "por qué" no sea obvio, por sobre trucos u optimizaciones prematuras.

## Alcance ético

- No scrapear LinkedIn bajo ninguna circunstancia.
- No automatizar publicaciones ni comentarios en ninguna red social.
- El scraping debe apuntar a fixtures locales o sitios de demostración/prueba, con bajo volumen,
  rate limiting y respeto de `robots.txt` cuando el objetivo sea un sitio real.
