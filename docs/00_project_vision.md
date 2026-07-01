# Visión del proyecto

## Visión

`retail-scraping-lab` es un laboratorio educativo y profesional para practicar y demostrar
scraping aplicado a inteligencia de productos y precios en retail. El proyecto simula, de forma
controlada y ética, el tipo de sistema que una empresa de e-commerce o retail usaría para
monitorear precios y disponibilidad de productos propios o de la competencia.

No busca ser "otro scraper" suelto: busca ser un sistema pequeño pero completo, con una
arquitectura clara, un modelo de datos pensado para responder preguntas de negocio, tests,
CI/CD y un dashboard de análisis.

## Objetivo de portfolio

El proyecto está pensado para:

- Servir como repositorio público de portfolio en GitHub, mostrando código profesional,
  documentado y testeado.
- Documentar el proceso de construcción en LinkedIn, mostrando no solo el resultado sino el
  razonamiento detrás de las decisiones técnicas (Spec-Driven Development, ADRs, uso de
  agentes de IA).
- Servir como evidencia concreta de habilidades de Python avanzado, SQL, modelado de datos,
  administración de proyectos y uso profesional de herramientas de IA, en el marco de la
  Tecnicatura en Desarrollo de Software y la búsqueda de roles como Data Engineer / Backend
  Developer.

## Valor para el negocio

Un sistema de este tipo, llevado a producción, permitiría a un equipo de negocio:

- Detectar cambios de precio en productos propios o de competidores.
- Monitorear disponibilidad de stock.
- Identificar categorías con mayor variación de precios.
- Detectar errores de extracción que indiquen cambios en la estructura de un sitio.
- Analizar la evolución histórica de precios para tomar decisiones de pricing.

Ver `docs/05_business_questions.md` para el detalle de las preguntas de negocio que el proyecto
busca responder.

## Valor técnico

El proyecto demuestra:

- Diseño de una arquitectura en capas (cliente HTTP, parser, validación, pipeline, repositorio,
  servicios, analytics, dashboard).
- Modelado de datos relacional pensado para análisis histórico (snapshots, no solo estado actual).
- Uso de SQL y SQLAlchemy para persistencia y consultas analíticas.
- Buenas prácticas de ingeniería: tipado estático, linting, tests automatizados, CI/CD.
- Un flujo de trabajo guiado por especificaciones (SDD), documentado en
  `docs/01_sdd_process.md`.
- Uso crítico y documentado de agentes de IA como aceleradores de desarrollo, no como caja negra.

## Alcance inicial

- Un scraper "demo" que trabaja sobre un fixture HTML local (no un sitio real todavía).
- Cliente HTTP con `requests`, parser con `lxml`, validación con Pydantic.
- Pipeline de exportación a JSON/CSV.
- Base del modelo de datos con SQLAlchemy (sin persistencia completa todavía).
- Dashboard mínimo en Streamlit que lee un archivo de ejemplo.
- CI básica (lint, typecheck, tests) y un workflow manual de scraping demo.

## Fuera de alcance (por ahora)

- Scraping de sitios reales de retail a gran escala.
- Scraping o automatización de cualquier tipo sobre LinkedIn u otras redes sociales.
- Persistencia completa en base de datos productiva y despliegue del dashboard en un servidor.
- Sistemas de proxies, rotación de IPs o técnicas de evasión de bloqueos.
- Alertas automáticas, notificaciones o integraciones con sistemas externos.

Estas capacidades podrán incorporarse en etapas futuras, cada una con su propia spec en
`specs/`, siguiendo el proceso descrito en `docs/01_sdd_process.md`.
