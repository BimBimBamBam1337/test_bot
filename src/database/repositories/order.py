from datetime import datetime

from .base import BaseRepository
from src.database.models import Order, OrderItem
from src.database.models import OrderStatus


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session):
        super().__init__(Order, session)

    async def create_from_cart(
        self, user_id: int, cart_items: list, contact_info: dict
    ):
        order = Order(
            user_id=user_id,
            status=OrderStatus.NEW,
            created_at=datetime.now(),
            contact_info=contact_info,
        )
        self.session.add(order)
        await self.session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id, product_id=item.product_id, quantity=item.quantity
            )
            self.session.add(order_item)

        await self.session.commit()
        return order
