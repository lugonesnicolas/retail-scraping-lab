# Reglas para agentes de IA

Este documento define reglas generales para cualquier agente de IA (ChatGPT, Claude Code, Codex,
Gemini Pro u otro) que colabore en `retail-scraping-lab`. Ver también `docs/06_ai_agents_usage.md`
para el detalle de qué herramienta se usa para qué tarea.

## Antes de modificar código

1. Leer `README.md` para entender el propósito del proyecto.
2. Leer la documentación relevante en `docs/` (especialmente `02_architecture.md` y
   `03_data_model.md` si el cambio toca esas áreas).
3. Leer la spec correspondiente en `specs/<feature>/spec.md`, `plan.md` y `tasks.md` antes de
   escribir código para esa feature.

## Cómo trabajar

- Trabajar por tareas pequeñas y verificables, siguiendo `tasks.md` de la spec activa.
- Antes de hacer un refactor grande (mover archivos, cambiar la forma de una API interna,
  reemplazar una dependencia), proponer el cambio y esperar confirmación en vez de aplicarlo
  directamente.
- Mantener la separación de responsabilidades entre cliente HTTP, parser, validación, pipeline,
  repositorio, servicios y dashboard. No colapsar capas por comodidad.
- Escribir código claro y con tipado explícito (type hints) en funciones y clases públicas.
- Agregar tests para la lógica nueva. Los tests no deben depender de internet.
- Explicar las decisiones técnicas relevantes en el mensaje de commit/PR o, si son
  arquitectónicas, proponer un ADR nuevo en `docs/adr/`.

## Límites de seguridad y alcance

- No exponer secretos, tokens ni credenciales en código, logs o documentación. Usar `.env`
  (nunca commiteado) y `.env.example` como referencia.
- No scrapear LinkedIn.
- No automatizar publicaciones ni comentarios en LinkedIn ni en ninguna otra red social.
- Usar `requests` y `lxml` como stack inicial de scraping. No reemplazar estas dependencias base
  (ni agregar `httpx`/`beautifulsoup4`) sin justificarlo explícitamente y, si el cambio es
  estructural, documentarlo con un ADR.
- El scraping debe ser de bajo volumen, con rate limiting, respetando `robots.txt` cuando el
  objetivo sea un sitio real, y sin extraer datos sensibles o personales.
