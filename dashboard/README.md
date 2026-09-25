# Dashboard

Dashboard en Streamlit que lee directamente de la base SQLite (a través de
`retail_scraping_lab.analytics.queries`) y muestra el estado histórico real del catálogo, no solo
el último export JSON/CSV. Ver `docs/03_data_model.md` para el modelo de datos y
`docs/05_business_questions.md` para las preguntas de negocio que responde.

## Cómo correrlo

1. Generar el histórico de ejemplo: `make run-demo` (ingiere las capturas del catálogo demo; se
   puede correr varias veces sin duplicar datos).
2. Levantar el dashboard: `make dashboard`.
3. Abrir la URL local que muestra Streamlit en la terminal (por defecto,
   http://localhost:8501).

Si la base de datos todavía no existe, el dashboard no rompe: muestra un aviso con los comandos
para generarla. Si la base existe pero no tiene productos, muestra un aviso más específico. Si la
base se creó con una versión anterior del esquema, recrearla con `make reset-db`.

## Configuración

La ruta de la base de datos se toma de `RSL_DATABASE_URL` (ver `Settings` en
`config/settings.py`), la misma variable que usa el CLI. Por defecto:
`sqlite:///./data/processed/retail_scraping_lab.db`.

## Secciones

Todas las fechas están en UTC.

- **Overview**: total de productos, total de snapshots, precio promedio actual (sobre el último
  snapshot de cada producto) y disponibilidad en tres estados (en stock / sin stock /
  desconocida).
- **Latest products**: último snapshot de cada producto, con fuente, marca, precio, moneda,
  disponibilidad, fecha de observación y URL.
- **Price changes**: productos cuyo precio cambió entre sus dos observaciones más recientes, con
  variación absoluta y porcentual.
- **Price history**: selector de producto y gráfico de evolución de su precio a lo largo del
  tiempo.
- **Scrape runs**: últimas corridas (una por captura), con su estado (`success`, `partial`,
  `failed`), ítems encontrados, productos nuevos/existentes, snapshots omitidos y errores.
- **Errors**: errores de extracción registrados (por ejemplo, un precio que no se pudo
  interpretar).

## Limitaciones de esta versión

- No hay filtros por categoría ni por fuente (el proyecto todavía trabaja con una sola fuente
  demo).
- El gráfico de evolución de precio es por producto individual, no agregado por categoría.
- No hay autenticación ni control de acceso; pensado para uso local.

Ver `docs/adr/0004-use-streamlit-dashboard.md` para la justificación de Streamlit como tecnología
y `specs/005-dashboard/` para el detalle funcional de esta etapa.
