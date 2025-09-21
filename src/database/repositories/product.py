from src.database.models import Product
from .base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(Product, session)
