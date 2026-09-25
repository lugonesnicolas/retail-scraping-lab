# Tasks 007: Historical Snapshots

- [x] Modelo: `ProductSnapshot.availability` (enum como texto), `UniqueConstraint(product_id,
      scraped_at)`, `ScrapeRun.snapshots_skipped` y `reset_db`.
- [x] Repositorio: `captured_at` como `scraped_at`, snapshots omitidos (`SaveResult`) y `brand`.
- [x] Service: un run por captura, errores persistidos, estado `success`/`partial`/`failed` y
      corrección del rollback.
- [x] Export con nombre determinístico por captura (`filename_stem`).
- [x] CLI: `scrape-demo` sobre todas las capturas (o `--capture`), resumen por captura y
      `init-db --reset`.
- [x] Makefile: `run-demo` con `--persist`, `reset-db` y `check`.
- [x] Analytics: columnas nuevas en `latest_snapshots`, disponibilidad en 3 estados y
      `price_changes`.
- [x] Dashboard: columnas, sección "Price changes" y rótulo UTC.
- [x] Tests: repositorio, queries, integración de 3 capturas, idempotencia, run `partial`,
      regresión del rollback, CLI y smoke test del dashboard.
- [x] Documentación: `docs/03_data_model.md`, `docs/05_business_questions.md`, `README.md` y
      `dashboard/README.md`.
- [x] Verificar `make check`, `make reset-db`, `make run-demo` (dos veces) y `make dashboard`.
