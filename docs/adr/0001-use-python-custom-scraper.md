# ADR 0001: Construir un scraper propio en Python en vez de usar un framework

## Estado

Aceptado.

## Contexto

El proyecto necesita extraer datos estructurados de páginas HTML (productos, precios,
disponibilidad). Existen frameworks especializados de scraping (por ejemplo, Scrapy) que
resuelven concurrencia, colas, middlewares y exportación de forma integrada.

Sin embargo, el objetivo principal del proyecto no es maximizar throughput de scraping, sino
demostrar arquitectura clara, modelado de datos, SQL y buenas prácticas de ingeniería, de forma
que cada capa sea fácil de explicar y de testear de forma aislada, en un proyecto de portfolio
deliberadamente pequeño.

## Decisión

Se construye un scraper propio, simple, basado en módulos de Python estándar del ecosistema
(`requests` + `lxml`), en vez de adoptar un framework de scraping completo.

## Alternativas consideradas

- **Scrapy**: framework maduro y potente, pero introduce su propio modelo de ejecución
  (asíncrono, basado en Twisted) y convenciones propias que dificultan mostrar una arquitectura
  en capas explícita y fácil de razonar como caso de estudio de portfolio.
- **Librerías de scraping "todo en uno"**: simplifican el desarrollo inicial pero ocultan
  decisiones (parsing, manejo de errores, rate limiting) que el proyecto busca justamente
  exponer y documentar.

## Consecuencias

- Mayor control y transparencia sobre cada etapa del proceso (request, parsing, validación,
  exportación), alineado con el objetivo de portfolio del proyecto.
- Mayor responsabilidad propia sobre aspectos que un framework resolvería (concurrencia,
  reintentos, rate limiting), que se irán incorporando de forma incremental y documentada.
- Facilita testear cada capa de forma aislada con `pytest`, sin depender de un runtime
  específico de scraping.
