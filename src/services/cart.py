from src.database.uow import UnitOfWork
from src.database.models import Cart


class CartService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def add_product(
        self, user_id: int, product_id: int, quantity: int, price: float
    ):
        async with self.uow as uow:
            return await uow.carts_repo.add_or_update(
                user_id, product_id, quantity, price
            )

    async def remove_product(self, user_id: int, product_id: int):
        async with self.uow as uow:
            await uow.carts_repo.remove_item(user_id, product_id)

    async def update_quantity(self, user_id: int, product_id: int, quantity: int):
        async with self.uow as uow:
            await uow.carts_repo.update_quantity(user_id, product_id, quantity)

    async def get_cart(self, user_id: int):
        async with self.uow as uow:
            cart = await uow.carts_repo.get_by_user(user_id)
            return cart

    async def get_total(self, user_id: int):
        cart = await self.get_cart(user_id)
        if not cart:
            return 0
        return sum(item.quantity * float(item.price_at_add) for item in cart.items)
