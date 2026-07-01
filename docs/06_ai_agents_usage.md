# Uso de agentes de IA en el proyecto

Este documento explica cómo se usan las distintas herramientas de IA en `retail-scraping-lab`,
como parte del enfoque de Spec-Driven Development descrito en `docs/01_sdd_process.md`.

## Para qué sirve cada herramienta

- **ChatGPT**: exploración de ideas, redacción y revisión de documentación (README, docs,
  specs), y como caja de resonancia para decisiones de diseño antes de formalizarlas.
- **Claude Code**: implementación de código dentro del repositorio, siguiendo las specs y las
  reglas de `CLAUDE.md`. Es el agente principal para escribir, refactorizar y testear código.
- **Codex**: generación y revisión de fragmentos de código puntuales, y como segunda opinión
  sobre implementaciones ya escritas.
- **Gemini Pro**: investigación técnica, comparación de enfoques y revisión cruzada de
  decisiones de arquitectura antes de documentarlas como ADR.

En la práctica, distintas tareas pueden resolverse con cualquiera de estas herramientas; la
lista anterior refleja el uso principal previsto, no una restricción estricta.

## Qué tareas puede hacer un agente

- Redactar borradores de `spec.md`, `plan.md` y `tasks.md` a partir de una descripción funcional.
- Implementar código siguiendo un plan ya acordado.
- Generar tests para lógica ya implementada.
- Sugerir mejoras de legibilidad, tipado o manejo de errores sobre código existente.
- Redactar o actualizar documentación (`docs/`, `README.md`) cuando el código cambia.

## Qué tareas deben ser revisadas por el desarrollador

- Cualquier decisión que agregue una dependencia nueva al proyecto.
- Cualquier cambio de arquitectura (nuevas capas, cambios en el modelo de datos).
- Cualquier código que toque el alcance ético del proyecto (scraping de fuentes nuevas,
  manejo de datos personales).
- Todo merge de código generado por un agente: debe pasar lint, typecheck y tests, y el
  desarrollador debe poder explicar qué hace y por qué.

## Reglas para no aceptar código sin entenderlo

- No copiar/pegar código generado por un agente sin leerlo línea por línea al menos una vez.
- Si una parte del código generado no se entiende, pedirle al agente que la explique antes de
  aceptarla, o reescribirla de forma más simple.
- Preferir que el agente explique el razonamiento detrás de una sugerencia (por qué esa
  estructura, por qué esa librería) antes de aplicarla, especialmente en decisiones de
  arquitectura o modelo de datos.
- Registrar en un ADR las decisiones de arquitectura relevantes, aunque hayan sido sugeridas por
  un agente, escritas con las propias palabras del desarrollador.
- Mantener siempre la capacidad de explicar el proyecto completo sin depender de la IA presente
  en la conversación: ese es el criterio de "portfolio defendible" del proyecto.
