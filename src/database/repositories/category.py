from .base import BaseRepository
from src.database.models import Category


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session):
        super().__init__(Category, session)
        self.session = session
