from .base import BaseRepository
from src.database.models import Order


class OrderRepository(BaseRepository[Order]):
    def __init__(self):
        super().__init__(Order)
