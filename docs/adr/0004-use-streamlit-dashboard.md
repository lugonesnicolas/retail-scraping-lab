# ADR 0004: Usar Streamlit para el dashboard

## Estado

Aceptado.

## Contexto

El proyecto necesita una forma visual de mostrar los datos scrapeados y responder las preguntas
de negocio de `docs/05_business_questions.md`: cantidad de productos, precio promedio, tabla de
productos y disponibilidad. El dashboard debe ser fácil de correr localmente y de mostrar como
parte del portfolio (capturas, video corto, demo en vivo).

## Decisión

Se usa Streamlit para construir el dashboard (`dashboard/app.py`), leyendo datos desde un
CSV/JSON exportado por el pipeline (y, a futuro, desde la base de datos vía `analytics/`).

## Alternativas consideradas

- **Un backend + frontend separados (por ejemplo, FastAPI + React)**: mucho más flexible y
  "production-grade", pero agrega complejidad y tiempo de desarrollo que no aporta al objetivo
  actual del proyecto (mostrar el análisis de datos, no construir una aplicación web completa).
- **Notebooks de Jupyter**: buenos para exploración, pero menos presentables como producto final
  de portfolio y más difíciles de versionar de forma limpia.
- **Dash / Panel**: alternativas válidas, pero Streamlit tiene una curva de aprendizaje más baja
  y es ampliamente reconocido en el ecosistema de Python para dashboards de datos.

## Consecuencias

- Un dashboard funcional se puede construir con muy poco código, usando `pandas` para leer y
  transformar los datos.
- Streamlit acopla la lógica de presentación a Python, lo cual es consistente con el resto del
  stack del proyecto.
- Si el proyecto evoluciona hacia una aplicación con más usuarios o necesidades de personalización
  de UI avanzada, se evaluará una arquitectura backend/frontend separada en un ADR futuro.

## Actualización (v0.1.0)

La lectura de CSV/JSON fue la primera iteración. Desde `005-dashboard`, el dashboard lee la base
SQLite exclusivamente a través de `analytics/queries.py`: funciones de solo lectura que devuelven
dataclasses y se testean de forma aislada. El dashboard no contiene SQL ni lógica de negocio, solo
presentación. La decisión de usar Streamlit se mantiene.
