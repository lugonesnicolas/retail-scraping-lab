# Spec 005: Dashboard

## Objetivo funcional

Construir un dashboard mínimo en Streamlit que permita visualizar los productos scrapeados,
respondiendo de forma visual algunas de las preguntas de `docs/05_business_questions.md`.

## Criterios de aceptación

- `dashboard/app.py` lee un archivo CSV/JSON generado por el pipeline (`data/exports/`) usando
  `pandas`.
- El dashboard muestra, como mínimo:
  - cantidad total de productos;
  - precio promedio;
  - tabla de productos (nombre, precio, moneda, disponibilidad, URL);
  - desglose de disponibilidad (cuántos productos `in_stock` vs `out_of_stock`, por ejemplo).
- El dashboard corre localmente con `make dashboard` sin errores, usando datos de ejemplo
  generados por `make run-demo`.

## Fuera de alcance de esta spec

- Autenticación o control de acceso.
- Consultas analíticas avanzadas (evolución histórica de precios) hasta que `003-data-model` y
  `analytics/queries.py` estén más desarrollados.
- Despliegue del dashboard en un servicio externo.
