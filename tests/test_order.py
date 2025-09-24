import pytest
from src.services import OrderService


@pytest.mark.asyncio
async def test_create_order(uow):
    order_service = OrderService(uow)

    user = await uow.users_repo.create(
        {"telegram_id": 1, "name": "old", "phone": "000", "address": "old address"}
    )
    await uow.carts_repo.create({"user_id": user.id})

    order = await order_service.create_order(
        order_number="1", user_id=user.id, delivery_method="courier"
    )

    assert order is not None
    assert order.user_id == user.id
    assert order.delivery_method == "courier"
