# ADR 0003: Usar SQLite como base de datos inicial

## Estado

Aceptado.

## Contexto

El modelo de datos (`docs/03_data_model.md`) necesita persistencia relacional para
`source`, `category`, `product`, `product_snapshot`, `scrape_run` y `scrape_error`. El proyecto
es un laboratorio de portfolio, ejecutado localmente y en GitHub Actions, sin infraestructura de
base de datos propia ni usuarios concurrentes reales.

## Decisión

Se usa SQLite como base de datos inicial, accedida a través de SQLAlchemy, con la URL de
conexión configurable vía `pydantic-settings` (`RSL_DATABASE_URL`).

## Alternativas consideradas

- **PostgreSQL**: motor más robusto y con más funcionalidades (tipos avanzados, concurrencia
  real), pero requiere infraestructura adicional (servidor, contenedor) que no aporta valor en
  esta etapa y agrega fricción para quien clone el repositorio y quiera correrlo localmente.
- **Sin base de datos (solo archivos JSON/CSV)**: más simple, pero no permite demostrar
  modelado relacional ni consultas SQL, que son parte de las habilidades que el proyecto busca
  mostrar.

## Consecuencias

- Cualquiera puede clonar el repositorio y correr el proyecto sin instalar ni configurar un
  servidor de base de datos.
- El uso de SQLAlchemy como capa de abstracción permite migrar a PostgreSQL (u otro motor) en el
  futuro cambiando principalmente la URL de conexión y el ADR correspondiente, sin reescribir el
  modelo de datos ni los repositorios.
- SQLite tiene limitaciones de concurrencia y de algunos tipos de datos avanzados, aceptables
  para el volumen y el uso previstos en este proyecto.
