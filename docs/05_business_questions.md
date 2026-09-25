# Preguntas de negocio

El modelo de datos (`docs/03_data_model.md`) y las capas de `analytics/` y `dashboard/` están
diseñadas para responder las siguientes preguntas de negocio:

- ¿Cuántos productos y snapshots hay en total? — `analytics.queries.count_products`,
  `count_snapshots`; sección "Overview" del dashboard.
- ¿Qué productos están disponibles actualmente y cuáles están agotados (`out_of_stock`)? —
  `latest_snapshots`, `current_availability_breakdown`; secciones "Overview" y "Latest products".
- ¿Cuál es el precio actual (último conocido) de cada producto? — `latest_snapshots`,
  `average_current_price`; secciones "Overview" y "Latest products".
- ¿Cómo evolucionan los precios de un producto a lo largo del tiempo? — `price_history`; sección
  "Price history" del dashboard.
- ¿Cuáles fueron las últimas corridas de scraping y qué resultado tuvieron? — `recent_scrape_runs`;
  sección "Scrape runs".
- ¿Qué errores de extracción ocurrieron recientemente? — `recent_errors`; sección "Errors".

Preguntas que todavía no están implementadas y quedan para una etapa futura (requieren, por
ejemplo, comparar corridas específicas o agrupar por categoría):

- ¿Qué productos cambiaron de precio entre dos corridas de scraping (o en un rango de fechas)?
- ¿Qué categorías presentan mayor variación de precio (volatilidad) en el tiempo?
- ¿Qué productos tienen errores de extracción recurrentes, y qué tipo de error es más frecuente?

Estas preguntas guían tanto el diseño del modelo de datos (por qué existe `product_snapshot`
separado de `product`) como las consultas de `analytics/queries.py` y las visualizaciones de
`dashboard/app.py`. Nuevas preguntas de negocio que surjan durante el desarrollo deberían
agregarse a esta lista y, si requieren cambios de modelo, documentarse con una spec o un ADR.
