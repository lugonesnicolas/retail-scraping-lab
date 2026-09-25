# ADR 0002: Usar `requests` y `lxml` como stack inicial de scraping

## Estado

Aceptado.

## Contexto

El proyecto necesita (1) un cliente HTTP para obtener HTML y (2) un mecanismo de parsing para
extraer datos estructurados de ese HTML. Existen varias alternativas populares en el ecosistema
Python: `httpx` (cliente HTTP moderno con soporte async) y `beautifulsoup4` (parser HTML de alto
nivel), entre otras.

## Decisión

El proyecto arranca con `requests` para HTTP y `lxml` para parsing, de forma explícita y como
parte del stack obligatorio inicial.

### Por qué `requests` y no `httpx`

- `requests` es la librería HTTP más establecida y familiar del ecosistema Python, con una API
  simple y ampliamente documentada.
- El proyecto no necesita, en esta etapa, soporte async ni HTTP/2; el volumen de requests es bajo
  (fixtures locales o sitios de demostración con pocas páginas).
- Priorizar `requests` mantiene el foco en la claridad de la arquitectura por sobre la
  optimización de I/O, que no es el objetivo actual del proyecto.

### Por qué `lxml` y no `beautifulsoup4`

- `lxml` ofrece parsing más rápido que `beautifulsoup4` al estar basado en `libxml2`.
- `lxml` permite usar XPath, lo que da control explícito y preciso sobre qué nodo se está
  extrayendo, algo valioso para un proyecto que busca mostrar criterio técnico en la extracción
  de datos.
- Usar XPath de forma explícita (en vez de selectores de alto nivel) obliga a razonar la
  estructura del HTML, lo cual refuerza el valor del proyecto como caso de estudio de portfolio.

## Ventajas de `requests`

- Simplicidad: API mínima y directa (`requests.get`, `requests.Session`).
- Estabilidad: librería madura, con años de uso en producción en el ecosistema.
- Familiaridad: es la librería HTTP que la mayoría de desarrolladores Python ya conoce.
- Suficiente para scraping HTTP básico: cubre timeouts, headers, sesiones y manejo de errores
  sin necesidad de funcionalidades async.

## Ventajas de `lxml`

- Parsing rápido, adecuado incluso si el proyecto crece en volumen de páginas.
- XPath como mecanismo de extracción explícito y potente.
- Control más fino sobre la estructura del documento que un parser de alto nivel.

## Trade-offs

- Menor abstracción que `beautifulsoup4` (que ofrece una API más "amigable" para principiantes)
  o que `httpx` (que resolvería concurrencia de forma más directa).
- Más responsabilidad del desarrollador: hay que escribir XPath explícitos y manejar
  concurrencia/async manualmente si en el futuro se necesita.
- Si el proyecto evoluciona hacia scraping de alto volumen o sitios con JavaScript dinámico, se
  evaluará incorporar herramientas adicionales (por ejemplo, un motor de renderizado headless),
  documentando esa decisión en un ADR nuevo en su momento. Esto no invalida la decisión actual,
  que responde al alcance definido en `docs/00_project_vision.md`.

## Restricciones explícitas

- No se incorpora `httpx` en esta etapa del proyecto.
- No se incorpora `beautifulsoup4` en esta etapa del proyecto.

Cualquier cambio a esta decisión requiere un ADR nuevo que la reemplace o la extienda.
