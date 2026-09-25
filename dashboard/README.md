# Dashboard

Dashboard en Streamlit que lee directamente de la base SQLite (a través de
`retail_scraping_lab.analytics.queries`) y muestra el estado histórico real del catálogo, no solo
el último export JSON/CSV. Ver `docs/03_data_model.md` para el modelo de datos y
`docs/05_business_questions.md` para las preguntas de negocio que responde.

## Cómo correrlo

1. Crear la base de datos si todavía no existe: `make init-db`.
2. Generar datos de ejemplo persistidos: `python -m retail_scraping_lab.cli scrape-demo --persist`
   (se puede correr varias veces para acumular más de un snapshot por producto).
3. Levantar el dashboard: `make dashboard`.
4. Abrir la URL local que muestra Streamlit en la terminal (por defecto,
   http://localhost:8501).

Si la base de datos todavía no existe, el dashboard no rompe: muestra un aviso con los comandos
de arriba. Si la base existe pero no tiene productos, muestra un aviso más específico sugiriendo
correr `scrape-demo --persist`.

## Configuración

La ruta de la base de datos se toma de `RSL_DATABASE_URL` (ver `Settings` en
`config/settings.py`), la misma variable que usa el CLI. Por defecto:
`sqlite:///./data/processed/retail_scraping_lab.db`.

## Secciones

- **Overview**: total de productos, total de snapshots, precio promedio actual (sobre el último
  snapshot de cada producto) y disponibles vs. no disponibles.
- **Latest products**: tabla con el último snapshot de cada producto (nombre, precio, moneda,
  disponibilidad, fecha de scraping).
- **Price history**: selector de producto y gráfico de evolución de su precio a lo largo del
  tiempo.
- **Scrape runs**: últimas corridas de scraping, con su estado, productos encontrados/insertados/
  actualizados y cantidad de errores.
- **Errors**: tabla de errores de extracción recientes, si existen.

## Limitaciones de esta versión

- No hay filtros por categoría ni por fuente (el proyecto todavía trabaja con una sola fuente
  demo).
- El gráfico de evolución de precio es por producto individual, no agregado por categoría.
- No hay autenticación ni control de acceso; pensado para uso local.

Ver `docs/adr/0004-use-streamlit-dashboard.md` para la justificación de Streamlit como tecnología
y `specs/005-dashboard/` para el detalle funcional de esta etapa.
