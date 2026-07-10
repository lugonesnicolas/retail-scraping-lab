# Plan 003: Data Model

## Enfoque técnico

- Usar `sqlalchemy.orm.DeclarativeBase` como base declarativa en `models/database.py`, con
  `Mapped[...]`/`mapped_column`/`relationship` para cada entidad (`Source`, `Category`,
  `Product`, `ProductSnapshot`, `ScrapeRun`, `ScrapeError`).
- Exponer `get_engine(database_url)`, `get_session_factory(engine)`, `init_db(engine)` (crea
  tablas vía `Base.metadata.create_all`, y el directorio contenedor si la URL es un archivo
  SQLite) y `get_session(session_factory)` (context manager con commit/rollback), para poder
  inicializar la base tanto en tests (SQLite en memoria) como en uso local (archivo SQLite en
  `data/processed/`).
- `repositories/product_repository.py` recibe una sesión de SQLAlchemy inyectada (no la crea
  internamente), para facilitar tests con una sesión en memoria. Cada método hace una operación
  simple (get-or-create, insert, update de estado); `save_scraped_products` es el único método
  que itera una lista, y delega en los métodos anteriores.
- `services/scraping_service.py` gana un flag `persist` y un `session_factory` opcional: si
  `persist=True`, crea un `ScrapeRun`, guarda productos + snapshots vía el repositorio, y
  registra un `ScrapeError` si algo falla durante el guardado, sin dejar de exportar JSON/CSV
  como hasta ahora.
- `cli.py` agrega el comando `init-db` y un flag `--persist` a `scrape-demo`. Como `cli.py` deja
  de tener un único comando, `make run-demo` pasa a invocar `scrape-demo` explícitamente (antes
  dependía del auto-invoke de Typer para apps de un solo comando).

## Notas

Esta spec construye sobre la base ya creada en `001-project-foundation` (skeleton de
`models/database.py`) y no requirió cambios en la estructura de carpetas. El modelo de datos
final en `docs/03_data_model.md` amplía ligeramente el propuesto originalmente (por ejemplo,
`Product.brand`/`normalized_name`, `ProductSnapshot.list_price`/`discount_percentage`,
contadores en `ScrapeRun`) para reflejar campos que un pipeline de precios real necesitaría,
aunque el scraper demo actual no los complete todos (quedan `nullable`).
