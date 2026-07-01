# Plan 002: Product Scraper

## Enfoque técnico

- `scraping/clients/http_client.py`: clase `HttpClient` con un método `get(url: str) -> str`
  que use una `requests.Session` interna, aplique timeout y headers desde `Settings`, y traduzca
  `requests.RequestException` / status codes de error a `HttpClientError`.
- `scraping/parsers/product_parser.py`: función `parse_product(html: str, source_url: str) ->
  dict` que use `lxml.html.fromstring` y XPath para extraer `name`, `price`, `currency`,
  `availability`, `product_url`, `image_url`. Lanza `ParsingError` si falta un campo obligatorio.
- `models/product.py`: modelo Pydantic `Product` con los seis campos, tipos apropiados (`price`
  como `Decimal` o `float`, `availability` como `str` o `Enum` simple), y validadores mínimos
  (precio no negativo).
- `scraping/spiders/demo_store_spider.py`: función `run_demo_spider(html_source: str |
  pathlib.Path) -> list[Product]` que orquesta cliente (o lectura de archivo local) + parser +
  validación Pydantic, capturando errores por producto sin abortar todo el proceso.
- `scraping/pipelines/product_pipeline.py`: función `export_products(products: list[Product],
  output_dir: Path, format: Literal["json", "csv"]) -> Path` que serializa la lista y escribe el
  archivo, devolviendo la ruta generada.
- `cli.py`: comando Typer `scrape-demo` que llama al spider demo sobre el fixture o sobre un
  path pasado por argumento, y al pipeline para exportar, imprimiendo un resumen con `rich`.

## Fixture

`tests/fixtures/demo_product_page.html` contiene un HTML mínimo con la estructura necesaria para
extraer los seis campos, representando una página de producto de una tienda ficticia
("demo-store"), usada tanto por los tests como por el comando `run-demo`.
