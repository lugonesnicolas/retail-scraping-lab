# Plan 008: Release v0.1.0

## Enfoque técnico

- **README**: se reescribe completo con la narrativa del case study. Reutiliza los diagramas de
  `docs/02_architecture.md` y el modelo de `docs/03_data_model.md`, y enlaza a ellos para el
  detalle en lugar de duplicarlos. Incluye:
  - un mapeo explícito entre los campos del registro normalizado (`source`, `source_url`,
    `product_name`, `brand`, `price`, `currency`, `availability`, `captured_at`) y el modelo;
  - una tabla "pregunta de negocio → dónde se responde";
  - comandos equivalentes sin `make`, para entornos que no lo tienen (por ejemplo, Windows).
- **Dependencias**: se sube `streamlit>=1.35` a `streamlit>=1.49`. Se verificó descargando los
  wheels de 1.46 a 1.50: la firma de `st.dataframe` acepta `width: Width = "stretch"` recién
  desde 1.49.
- **CI**:
  - `ci.yml` suma un paso `ruff format --check .`;
  - `scrape.yml` pasa a subir `data/exports/` y `data/processed/` (la base SQLite) como un solo
    artefacto. `make run-demo` ya persiste desde `007`.
- **Docs**:
  - `00_project_vision.md` reescribe la visión y el alcance con el estado real;
  - `ADR 0004` y `ADR 0005` suman una sección de actualización, sin reescribir su historia;
  - en `.env.example` y `Settings` se reemplaza el placeholder `<usuario>` del User-Agent por el
    repo real.
- **CHANGELOG**: formato "Keep a Changelog", con la versión `0.1.0` agrupada por capa.
- **Verificación**: `git clone` del repo local a un directorio temporal. Ahí se crea un venv
  nuevo, se corren `make install`, `make check` y `make run-demo`, y el dashboard se levanta con
  AppTest y con un servidor real.
