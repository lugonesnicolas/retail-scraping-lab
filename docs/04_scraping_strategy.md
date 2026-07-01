# Estrategia de scraping

## Estrategia inicial: fixture / demo

La primera etapa del proyecto trabaja exclusivamente contra un fixture HTML local
(`tests/fixtures/demo_product_page.html`) y, opcionalmente, contra un sitio de demostración
público pensado para practicar scraping. El objetivo es validar la arquitectura (cliente →
parser → validación → pipeline) sin depender de la disponibilidad ni de las condiciones de uso
de un sitio real.

## Futura adaptación a sitios reales

Cuando el proyecto avance hacia sitios reales, se seguirá este criterio:

- Solo se scrapearán sitios públicos que lo permitan según sus términos de servicio y
  `robots.txt`, o sitios de demostración construidos específicamente para practicar scraping.
- Cada nueva fuente se agrega como un spider nuevo en `scraping/spiders/`, reutilizando el
  cliente HTTP y agregando un parser específico si la estructura HTML difiere.
- Cualquier extensión a un sitio real se documenta con su propia spec en `specs/`.

## Uso de `requests`

El cliente HTTP (`scraping/clients/http_client.py`) usa `requests` de forma simple y explícita:
una sesión configurable, timeout y headers (incluyendo `User-Agent`) parametrizables vía
`pydantic-settings`. Ver `docs/adr/0002-use-requests-and-lxml.md` para la justificación de por
qué se eligió `requests` sobre `httpx`.

## Uso de `lxml`

El parser (`scraping/parsers/product_parser.py`) usa `lxml` con XPath para extraer campos de
forma explícita y eficiente. Ver `docs/adr/0002-use-requests-and-lxml.md` para la justificación
de por qué se eligió `lxml` sobre `beautifulsoup4`.

## Rate limiting

- El scraping demo procesa un volumen bajo de páginas (fixtures o unas pocas páginas de un sitio
  de práctica).
- Cuando se scrapee un sitio real, se introducirá una pausa configurable entre requests
  (por ejemplo, vía `time.sleep` parametrizado en la configuración), evitando ráfagas de
  peticiones.

## Retries

- La primera versión del cliente HTTP no implementa retries automáticos; los errores se
  propagan como excepciones de dominio (`core/exceptions.py`) para que la capa que orquesta
  decida qué hacer.
- El cliente está diseñado para poder incorporar retries con backoff (por ejemplo, mediante
  `requests.adapters.HTTPAdapter` con `Retry`) en una iteración futura, sin cambiar su interfaz
  pública.

## Timeouts

- Todas las requests usan un timeout configurable (`RSL_HTTP_TIMEOUT_SECONDS` en `.env`), con un
  valor por defecto conservador, para evitar que el scraper quede colgado ante una fuente lenta
  o caída.

## `robots.txt`

- Cuando el objetivo sea un sitio real (no un fixture local), se revisará su `robots.txt` antes
  de scrapear, y se respetarán las rutas deshabilitadas para bots.
- Los fixtures locales y sitios de demostración construidos para practicar scraping no requieren
  esta verificación, pero se documentará igualmente la fuente utilizada.

## Manejo de errores

- Errores de red o HTTP (timeout, status code de error) se capturan en el cliente HTTP y se
  traducen a excepciones propias del dominio.
- Errores de parsing (campo faltante, estructura inesperada) se capturan en el parser y se
  registran como `scrape_error` (ver `docs/03_data_model.md`) en vez de interrumpir toda la
  corrida.
- El objetivo es que un error en un producto individual no aborte el scraping de los demás.

## Validaciones

- Todo producto parseado pasa por validación con Pydantic (`models/product.py`) antes de entrar
  al pipeline. Un producto que no cumple el esquema (por ejemplo, precio no numérico) se
  descarta y se registra como error, no se persiste con datos inconsistentes.
