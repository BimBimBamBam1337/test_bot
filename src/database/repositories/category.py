from sqlalchemy import select, delete
from src.database.models import Category
from .base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session):
        super().__init__(Category, session)
        self.session = session
