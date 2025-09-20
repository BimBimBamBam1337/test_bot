from src.database.models import OrderItem
from .base import BaseRepository


class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self):
        super().__init__(OrderItem)
