from datetime import datetime
from src.database.uow import UnitOfWork
from src.database.models import OrderStatus


class OrderService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    # Получить все заказы
    async def list_orders(self):
        async with self.uow as uow:
            return await uow.orders_repo.get_all()

    # Получить заказы конкретного пользователя
    async def list_user_orders(self, user_id: int):
        async with self.uow as uow:
            return await uow.orders_repo.get(user_id)

    # Получить один заказ по ID
    async def get_order(self, order_id: int):
        async with self.uow as uow:
            return await uow.orders_repo.get(order_id)

    # Создать заказ из корзины
    async def create_order(self, order_number: str, user_id: int, delivery_method: str):
        async with self.uow as uow:
            cart = await uow.carts_repo.get_by_user(user_id)
            if not cart:
                return None  # корзина пустая

            # создаём заказ
            order = await uow.orders_repo.create_from_cart(
                order_number,
                user_id,
                delivery_method,
                cart.items,
            )
            # очищаем корзину
            await uow.carts_repo.clear(user_id)
            return order

    # Обновить статус заказа
    async def update_order_status(self, order_id: int, status: OrderStatus):
        async with self.uow as uow:
            order = await uow.orders_repo.get(order_id)
            if not order:
                return None
            order.status = status
            await uow.session.commit()
            return order
