# Plan 003: Data Model

## Enfoque técnico

- Usar `sqlalchemy.orm.DeclarativeBase` como base declarativa en `models/database.py`.
- Modelar cada entidad de `docs/03_data_model.md` como una clase ORM, con tipos explícitos
  (`Mapped[...]`) y claves foráneas correspondientes.
- Exponer una función `get_engine(database_url: str)` y `init_db(engine)` (crea tablas vía
  `Base.metadata.create_all`) para poder inicializar la base tanto en tests (SQLite en memoria)
  como en uso local (archivo SQLite en `data/processed/`).
- `repositories/product_repository.py` recibe una sesión de SQLAlchemy inyectada (no la crea
  internamente), para facilitar tests con una sesión en memoria.

## Notas

Esta spec construye sobre la base ya creada en `001-project-foundation` (skeleton de
`models/database.py`) y no debería requerir cambios en la estructura de carpetas.
