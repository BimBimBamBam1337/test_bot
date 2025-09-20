from src.database.models import Cart
from .base import BaseRepository


class CartRepository(BaseRepository[Cart]):
    def __init__(self):
        super().__init__(Cart)
