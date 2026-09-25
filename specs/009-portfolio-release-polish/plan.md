# Plan 009: Portfolio release polish (v0.1.1)

## Enfoque técnico

- **README**: se reescribe en inglés sobre la base del README de `008`, verificando cada afirmación
  contra el código (`models/database.py`, `services/scraping_service.py`,
  `analytics/queries.py`). Aclara que la UI, el CLI y la documentación detallada están en
  español, y que la tabla `categories` existe en el esquema pero el pipeline todavía no la usa.
- **Screenshot**: se corre `make run-demo` sobre una base nueva y se levanta el dashboard con
  `streamlit run ... --client.toolbarMode viewer` (oculta el botón "Deploy" sin cambiar código).
  La captura se toma con un navegador headless externo al proyecto, sin agregar dependencias. El
  modo `--screenshot` de Chromium no sirve: captura el esqueleto de carga, porque Streamlit
  recibe los datos por websocket. Se usa entonces el CLI de Playwright vía `npx`, con una espera
  explícita.
- **Versiones**: se corrigen el README y el título de alcance en `docs/00_project_vision.md`. El
  CHANGELOG suma una sección `[Unreleased]` para estos cambios de documentación, que no cambian el
  paquete ni justifican una versión nueva.
- **`pyproject.toml`**: solo cambia `description`, que pasa a inglés, igual que la descripción de
  GitHub.
- **Metadata de GitHub**: `gh repo edit --description ... --add-topic ...`. El repo no tenía
  topics, así que no se borra ninguno.
- **Release**: el tag `v0.1.1` ya existe en origin y apunta al commit "Version 0.1.1". No se
  mueve: este pulido es solo de documentación y GitHub muestra el README de `main`.
