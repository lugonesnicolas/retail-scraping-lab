# Proceso de Spec-Driven Development (SDD)

## Qué significa SDD en este proyecto

Spec-Driven Development (SDD) es la práctica de escribir, antes de programar, una especificación
clara de qué se va a construir y por qué, seguida de un plan técnico y una lista de tareas
accionables. El código se escribe después, guiado por esos documentos, y la documentación del
proyecto se actualiza como parte del mismo trabajo.

En `retail-scraping-lab`, cada feature relevante vive en una carpeta dentro de `specs/`, con tres
archivos:

- `spec.md`: objetivo funcional de la feature y criterios de aceptación. Responde "qué" y "para
  qué", no "cómo".
- `plan.md`: enfoque técnico elegido para implementar la spec. Responde "cómo": qué módulos,
  clases, librerías y estructura de datos se van a usar.
- `tasks.md`: lista de tareas concretas y accionables derivadas del plan, en el orden en que se
  van a ejecutar.

## Flujo: spec → plan → tasks → código → tests → documentación

1. **Spec**: se define el objetivo funcional y los criterios de aceptación de la feature.
2. **Plan**: se traduce la spec en un enfoque técnico concreto, respetando la arquitectura
   descrita en `docs/02_architecture.md` y el stack definido en `pyproject.toml`.
3. **Tasks**: se descompone el plan en tareas pequeñas y verificables.
4. **Código**: se implementa cada tarea, siguiendo las reglas de `CLAUDE.md` y `AGENTS.md`.
5. **Tests**: se agregan tests para la lógica nueva, sin dependencia de internet.
6. **Documentación**: se actualiza `docs/`, ADRs y `README.md` si la feature cambió algo
   relevante de la arquitectura, el modelo de datos o el stack.

Este orden es una guía, no una burocracia rígida: para cambios muy pequeños (un typo, un ajuste
de configuración) no hace falta una spec completa. Para features nuevas o cambios de arquitectura,
sí.

## Cómo se usarán agentes de IA en este flujo

Los agentes de IA (ChatGPT, Claude Code, Codex, Gemini Pro) se usan en distintas etapas:

- Para ayudar a redactar y revisar specs, planes y tareas.
- Para generar código a partir de un plan ya definido y acordado.
- Para generar tests a partir de la lógica implementada.
- Para revisar código existente y sugerir mejoras (legibilidad, tipado, manejo de errores).

El detalle de qué herramienta se usa para qué está en `docs/06_ai_agents_usage.md`.

## Cómo evitar depender ciegamente de la IA

- Ninguna spec, plan o código generado por un agente se acepta sin revisión humana.
- El desarrollador debe poder explicar, sin ayuda del agente, qué hace cada parte del código
  aceptado y por qué se tomó esa decisión.
- Las decisiones de arquitectura relevantes se documentan en ADRs (`docs/adr/`), aunque hayan
  sido sugeridas por un agente, con la justificación en palabras del desarrollador.
- Se prioriza entender el "por qué" de una sugerencia antes de aplicarla, especialmente cuando
  implica agregar una dependencia nueva o cambiar la arquitectura existente.
- Los agentes no tienen permiso para tomar decisiones que toquen el alcance ético del proyecto
  (por ejemplo, scraping de LinkedIn) ni para agregar dependencias fuera del stack definido sin
  justificación explícita (ver `AGENTS.md`).
