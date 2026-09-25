# Visión del proyecto

## Visión

`retail-scraping-lab` es un sistema pequeño y completo de monitoreo de productos, precios y
disponibilidad en retail. Implementa el tipo de pipeline que un equipo de e-commerce o de pricing
usaría para seguir su propio catálogo o el de la competencia:

```
fuente → acquisition → parsing → normalization → validation → histórico en SQL → analytics
```

No busca ser "otro scraper": el valor está en lo que rodea a la extracción. Eso incluye capas
separadas y testeables, un modelo de datos histórico pensado para preguntas de negocio, una carga
idempotente con trazabilidad de cada corrida, tests automatizados, CI y un dashboard de análisis.

## Objetivo del repositorio

- Servir como engineering case study público: mostrar código documentado y testeado, junto con
  el razonamiento detrás de cada decisión (specs en `specs/`, ADRs en `docs/adr/`).
- Evidenciar habilidades de Python, data engineering, adquisición de datos, ETL, SQL/SQLAlchemy,
  validación de datos, modelado histórico, testing y CI.
- Mantenerse deliberadamente pequeño y demostrable. La arquitectura reutilizable para muchos
  scrapers a escala es el objetivo de otro proyecto (`ndevscrap`), no de este.

## Valor para el negocio

Un sistema de este tipo, llevado a producción, permitiría a un equipo de negocio:

- Detectar cambios de precio en productos propios o de competidores.
- Monitorear disponibilidad de stock.
- Saber de qué fuente proviene cada dato y cuándo fue observado.
- Detectar errores de extracción que indiquen cambios en la estructura de un sitio.
- Analizar la evolución histórica de precios para tomar decisiones de pricing.

Ver `docs/05_business_questions.md` para las preguntas concretas que responde hoy y las que
quedan para versiones futuras.

## Valor técnico

- Arquitectura en capas con contratos explícitos: acquisition (`ContentClient`), parsing,
  normalización, validación (Pydantic), repositorio, servicios, analytics y dashboard.
- Modelo relacional histórico (catálogo + snapshots) con carga idempotente garantizada por una
  restricción única, y trazabilidad de corridas y errores.
- Consultas SQL analíticas con SQLAlchemy, incluida una window function para la variación de
  precio.
- Tipado estático, linting, tests unitarios y de integración sin red, y CI en GitHub Actions.
- Un flujo de trabajo guiado por especificaciones (SDD), documentado en
  `docs/01_sdd_process.md`, con uso documentado de agentes de IA (`docs/06_ai_agents_usage.md`).

## Alcance actual (`v0.1.1`)

- Una fuente de datos: el catálogo demo `demo-store`, con tres capturas fechadas en
  `tests/fixtures/demo_store/`, leído a través de la capa de acquisition. Es offline y
  reproducible.
- Ingesta completa: parsing con `lxml`/XPath, normalización de precios y disponibilidad,
  validación con Pydantic y errores por ítem que no abortan la captura.
- Persistencia histórica en SQLite vía SQLAlchemy, con un run por captura (`success`, `partial`,
  `failed`).
- CLI (`scrape-demo`, `init-db`) y Makefile (`install`, `run-demo`, `dashboard`, `check`).
- Dashboard Streamlit sobre la capa de analytics.
- CI (lint, formato, tipos, tests) y un workflow manual que corre el pipeline y publica sus
  resultados.

## Fuera de alcance (por ahora)

- Scraping de sitios reales, múltiples retailers o scraping masivo.
- Navegadores headless (Playwright), proxies, rotación de IPs o técnicas anti-bot.
- Orquestadores, colas o infraestructura distribuida (Airflow, Kafka, Redis, Kubernetes).
- Base de datos servidor, migraciones de esquema, despliegue del dashboard y autenticación.
- Alertas automáticas o integraciones con sistemas externos.
- Scraping o automatización de cualquier tipo sobre LinkedIn u otras redes sociales.

Las capacidades que tengan sentido para este proyecto se incorporarán en versiones futuras, cada
una con su propia spec en `specs/` (ver el roadmap en `README.md`).
