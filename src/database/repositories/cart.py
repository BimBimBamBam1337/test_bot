from sqlalchemy import delete, select

from src.database.models import Cart
from .base import BaseRepository


class CartRepository(BaseRepository[Cart]):
    def __init__(self, session):
        super().__init__(Cart, session)
        self.session = session

    async def clear(self, user_id: int) -> None:
        """Удаляет все товары из корзины пользователя"""
        await self.session.execute(delete(Cart).where(Cart.user_id == user_id))
        await self.session.commit()

    async def get_by_user(self, user_id: int) -> list[Cart]:
        result = await self.session.execute(select(Cart).where(Cart.user_id == user_id))
        return list(result.scalars().all())
