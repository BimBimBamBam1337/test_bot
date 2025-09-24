from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from src.database.models import Order, OrderItem
from src.database.models import OrderStatus


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session):
        super().__init__(Order, session)

    async def get(self, obj_id: int):
        stmt = (
            select(Order)
            .options(selectinload(Order.user), selectinload(Order.items))
            .where(Order.id == obj_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self):
        stmt = select(Order).options(
            selectinload(Order.user), selectinload(Order.items)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_from_cart(
        self, order_number: str, user_id: int, delivery_method: str, cart_items: list
    ):
        order = Order(
            order_number=order_number,
            user_id=user_id,
            status=OrderStatus.NEW,
            delivery_method=delivery_method,
            created_at=datetime.now(),
            total=sum(float(item.price_at_add) * item.quantity for item in cart_items),
        )
        self.session.add(order)
        await self.session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price_at_add,
            )

            self.session.add(order_item)

        await self.session.commit()
        return order
