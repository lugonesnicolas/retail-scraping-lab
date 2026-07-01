# Dashboard

Dashboard mínimo en Streamlit que lee el export de productos más reciente generado en
`data/exports/` y muestra indicadores básicos: cantidad de productos, precio promedio,
disponibilidad y tabla de productos.

## Cómo correrlo

1. Generar datos de ejemplo: `make run-demo`.
2. Levantar el dashboard: `make dashboard`.
3. Abrir la URL local que muestra Streamlit en la terminal (por defecto,
   http://localhost:8501).

Ver `docs/adr/0004-use-streamlit-dashboard.md` para la justificación de esta elección técnica y
`specs/005-dashboard/` para el detalle funcional.
