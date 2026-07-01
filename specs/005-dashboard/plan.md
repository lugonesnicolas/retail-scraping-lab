# Plan 005: Dashboard

## Enfoque técnico

- `dashboard/app.py` usa `pandas.read_json` o `pandas.read_csv` sobre el archivo más reciente de
  `data/exports/` (o una ruta configurable), y `st.metric`, `st.dataframe` y un gráfico simple
  (`st.bar_chart`) de Streamlit para mostrar los indicadores mínimos requeridos por la spec.
- Se mantiene sin lógica de scraping ni de acceso a base de datos en esta primera versión; toda
  la lógica de negocio compleja se delega a `analytics/queries.py` en iteraciones futuras, una
  vez que `003-data-model` esté implementada.
