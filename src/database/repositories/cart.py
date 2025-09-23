from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from .base import BaseRepository
from src.database.models import Cart, CartItem


class CartRepository(BaseRepository[Cart]):
    def __init__(self, session):
        super().__init__(Cart, session)

    async def get_by_user(self, user_id: int):
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add_or_update(
        self, user_id: int, product_id: int, quantity: int = 1, price: float = 0
    ):
        cart = await self.get_by_user(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            self.session.add(cart)
            await self.session.flush()

        # ищем товар в корзине
        item = next((i for i in cart.items if i.product_id == product_id), None)
        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                price_at_add=price,
            )
            self.session.add(item)

        await self.session.flush()
        return item

    async def remove_item(self, user_id: int, product_id: int):
        cart = await self.get_by_user(user_id)
        if not cart:
            return
        item = next((i for i in cart.items if i.product_id == product_id), None)
        if item:
            await self.session.delete(item)
            await self.session.flush()

    async def update_quantity(self, user_id: int, product_id: int, quantity: int):
        cart = await self.get_by_user(user_id)
        if not cart:
            return
        item = next((i for i in cart.items if i.product_id == product_id), None)
        if item:
            item.quantity = quantity
            await self.session.flush()

    async def clear(self, user_id: int):
        cart = await self.get_by_user(user_id)
        if cart:
            for item in cart.items:
                await self.session.delete(item)
            await self.session.flush()
