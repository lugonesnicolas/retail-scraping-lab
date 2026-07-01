# Preguntas de negocio

El modelo de datos (`docs/03_data_model.md`) y las capas de `analytics/` y `dashboard/` están
diseñadas para responder, con el tiempo, las siguientes preguntas de negocio:

- ¿Qué productos cambiaron de precio entre dos corridas de scraping (o en un rango de fechas)?
- ¿Qué productos están disponibles actualmente y cuáles están agotados (`out_of_stock`)?
- ¿Qué categorías presentan mayor variación de precio (volatilidad) en el tiempo?
- ¿Qué productos tienen errores de extracción recurrentes, y qué tipo de error es más frecuente?
- ¿Cómo evolucionan los precios de un producto (o de una categoría) a lo largo del tiempo?

Estas preguntas guían tanto el diseño del modelo de datos (por qué existe `product_snapshot`
separado de `product`) como las consultas que se implementan en `analytics/queries.py` y las
visualizaciones que expone `dashboard/app.py`. Nuevas preguntas de negocio que surjan durante el
desarrollo deberían agregarse a esta lista y, si requieren cambios de modelo, documentarse con
una spec o un ADR.
