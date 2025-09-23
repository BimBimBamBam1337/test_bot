# cart_item_repository.py
from sqlalchemy import select, delete
from src.database.models import CartItem
from .base import BaseRepository


class CartItemRepository(BaseRepository[CartItem]):
    def __init__(self, session):
        super().__init__(CartItem, session)

    async def get_item(self, cart_id: int, product_id: int) -> CartItem | None:
        result = await self.session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id, CartItem.product_id == product_id
            )
        )
        return result.scalars().first()

    async def add_or_update(
        self, cart_id: int, product_id: int, quantity: int, price: float
    ):
        """Добавить товар в корзину или обновить количество"""
        item = await self.get_item(cart_id, product_id)
        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity,
                price_at_add=price,
            )
            self.session.add(item)
        await self.session.flush()
        return item

    async def update_quantity(self, cart_id: int, product_id: int, quantity: int):
        item = await self.get_item(cart_id, product_id)
        if item:
            item.quantity = quantity
            await self.session.flush()
        return item

    async def remove_item(self, cart_id: int, product_id: int):
        await self.session.execute(
            delete(CartItem).where(
                CartItem.cart_id == cart_id, CartItem.product_id == product_id
            )
        )
        await self.session.flush()
