# Spec 009: Portfolio release polish (v0.1.1)

## Objetivo funcional

Dejar la versión `0.1.1` presentable como proyecto de portfolio en GitHub y LinkedIn, sin tocar
la funcionalidad. Quien llega al repositorio tiene que entender en menos de 30 segundos qué
resuelve el proyecto, cómo está construido y que funciona.

## Criterios de aceptación

- **`README.md`** reescrito en inglés como engineering case study (no una traducción literal),
  en este orden: Problem → Solution → Architecture → Data Model → Engineering Decisions → Demo →
  Dashboard → Running Locally → Testing and Quality → Project Status → Repository Structure →
  Documentation.
  - Muestra `v0.1.1` como versión actual.
  - Sin framing educativo ni claims que el código no sostenga ("production ready", "enterprise
    grade", "highly scalable").
  - Todos los números (productos, snapshots, variaciones de precio) salen de una corrida real.
- **`LICENSE`** MIT, coherente con `license` en `pyproject.toml`.
- **`docs/assets/dashboard-overview.png`**: screenshot real del dashboard corriendo sobre los
  datos de la demo (no un mockup), enlazado desde el README.
- **Consistencia de versión**: ningún documento presenta `0.1.0` como la versión actual. Las
  referencias históricas (entrada `0.1.0` del CHANGELOG, spec `008`, notas de los ADRs) no se
  tocan.
- **Metadata de GitHub**: descripción en inglés y topics del stack.
- **Release**: se determina el estado del tag y de la GitHub Release `v0.1.1` y se deja preparado
  el comando; crearlos queda a cargo del desarrollador.
- **Verificación**: pasan `make check` y `make run-demo`.

## Fuera de alcance de esta spec

- Cualquier cambio funcional en el pipeline, el esquema, el dashboard o las dependencias.
- Traducir al inglés `docs/`, ADRs, specs, CHANGELOG o los textos de la UI/CLI.
- Crear o mover tags, publicar la GitHub Release, merge y push: los hace el desarrollador, o se
  hacen solo a pedido explícito.
