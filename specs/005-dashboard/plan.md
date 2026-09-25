# Plan 005: Dashboard

## Iteración 1 (completada)

- `dashboard/app.py` usaba `pandas.read_json` sobre el archivo más reciente de `data/exports/`, y
  `st.metric`, `st.dataframe` y `st.bar_chart` para los indicadores mínimos requeridos por esa
  versión de la spec. Sin lógica de scraping ni de acceso a base de datos.

## Iteración 2 (esta spec): lectura desde SQLite

### Enfoque técnico

- **`analytics/queries.py`**: funciones puras que reciben una `Session` de SQLAlchemy ya abierta
  y devuelven dataclasses simples (`LatestProductRow`, `PricePoint`, `ScrapeRunRow`,
  `ScrapeErrorRow`, `ProductOption`), no objetos ORM ni DataFrames — mantiene la capa de
  analytics independiente de cómo se presentan los datos (dashboard, CLI, tests). La consulta de
  "último snapshot por producto" (`latest_snapshots`) se centraliza en una sola función, ya que
  la usan tanto "Latest products" como el precio promedio y la disponibilidad actual en Overview.
- **`dashboard/app.py`**: obtiene la URL de la base desde `config/settings.get_settings()` (misma
  fuente que usa el CLI), abre una `Session` con `models.database.get_session` y llama a
  `analytics/queries.py` para cada sección. El `Engine` se cachea con `st.cache_resource` para no
  reabrir la conexión en cada rerun de Streamlit.
- **Manejo de "no hay datos"**: se resuelve en dos niveles. (1) si la base SQLite no existe como
  archivo (`Path.exists()` sobre la ruta parseada de la URL), se muestra un aviso y se corta con
  `st.stop()` antes de intentar conectar. (2) si la base existe pero no tiene productos, se
  detecta con `count_products() == 0` y se muestra un aviso más específico.
- **Gráfico de evolución de precio**: `st.line_chart` sobre un DataFrame con `price` casteado a
  `float` (los precios son `Decimal` en el modelo; Streamlit/Altair no infieren bien el tipo
  numérico de un `Decimal`).
- No se agrega Alembic, httpx, beautifulsoup4, Scrapy ni Playwright. No se toca el pipeline de
  export JSON/CSV.
