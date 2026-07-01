"""Repositorio de productos.

Skeleton inicial: la implementacion completa (operaciones sobre Source, Product,
ProductSnapshot, ScrapeRun) se aborda en la spec 003-data-model, una vez que los
modelos ORM de models/database.py esten definidos. Ver docs/03_data_model.md.
"""

from sqlalchemy.orm import Session


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
