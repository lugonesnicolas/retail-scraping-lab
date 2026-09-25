# Tasks 005: Dashboard

## Iteración 1 (completada)

- [x] Crear `dashboard/app.py` con lectura de datos de ejemplo y métricas mínimas.
- [x] Crear `dashboard/README.md` con instrucciones de uso.
- [x] Ejecutar `make run-demo` seguido de `make dashboard` y verificar visualmente los
      indicadores.

## Iteración 2: lectura desde SQLite

- [x] Implementar consultas analíticas en `src/retail_scraping_lab/analytics/queries.py` (total
      de productos, total de snapshots, último snapshot por producto, precio promedio actual,
      disponibilidad actual, historial de precio por producto, últimas corridas de scraping,
      errores recientes).
- [x] Agregar tests de `analytics/queries.py` en `tests/unit/test_queries.py` usando SQLite
      en memoria (fixture `db_session` existente).
- [x] Actualizar `dashboard/app.py` para leer desde SQLite vía `analytics/queries.py`, con aviso
      claro si la base no existe o no tiene datos todavía.
- [x] Agregar secciones Overview, Latest products, Price history, Scrape runs y Errors.
- [x] Actualizar documentación: `README.md`, `dashboard/README.md`,
      `docs/05_business_questions.md`, `specs/005-dashboard/spec.md`,
      `specs/005-dashboard/plan.md`, este archivo.
- [x] Verificar `make lint`, `make typecheck`, `make test`, `make run-demo`,
      `python -m retail_scraping_lab.cli init-db`, `scrape-demo --persist` y `make dashboard`
      (vía `streamlit.testing.v1.AppTest` y un server real) sin errores.
