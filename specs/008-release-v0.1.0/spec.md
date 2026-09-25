# Spec 008: Release v0.1.0

## Objetivo funcional

Cerrar la primera versión de portfolio del proyecto. La Definition of Done de `v0.1.0`:

> Una persona puede clonar el repositorio, ejecutar un pipeline completo de adquisición de
> productos, almacenar snapshots históricos, ejecutar los tests y visualizar los resultados en un
> dashboard sin necesitar conocimiento previo del código.

Las specs `006` y `007` completaron la funcionalidad. Esta spec cubre la presentación, la
reproducibilidad y la verificación final.

## Criterios de aceptación

- **`README.md`** como engineering case study, en este orden: Problema → Solución →
  Arquitectura → Modelo de datos → Decisiones de ingeniería → Cómo correrlo localmente →
  Testing → Demo → Dashboard → Estado del proyecto.
  - Sin framing de "laboratorio educativo" ni de "en formación".
  - Sin claims que el código no sostenga (no es "production ready").
  - Permite levantar el proyecto siguiendo solo el README.
- **`pyproject.toml`**: descripción actualizada, y un mínimo de `streamlit` compatible con la API
  que usa el dashboard (`st.dataframe(width="stretch")` requiere `>=1.49`, verificado sobre los
  wheels publicados).
- **`docs/00_project_vision.md`**: refleja el alcance real de `v0.1.0`. `ADR 0004` y `ADR 0005`
  registran cómo evolucionaron sus decisiones.
- **CI**: `ci.yml` también verifica el formato (`ruff format --check`). `scrape.yml` corre el
  flujo completo con persistencia y publica, como artefactos, los exports y la base SQLite.
- **`CHANGELOG.md`** con la entrada `0.1.0`.
- **Verificación final**: desde un clone limpio, siguiendo solo el README, pasan `make check` y
  `make run-demo`, y el dashboard renderiza los datos.

## Fuera de alcance de esta spec

- Tag `v0.1.0`, push y merge: los hace el desarrollador, o se hacen solo a pedido explícito.
- Funcionalidad nueva (fuentes HTTP reales, Alembic, scheduling): quedan en el roadmap.
