import pytest
from src.services import CartService


@pytest.mark.asyncio
async def test_add_item_to_cart(uow):
    cart_service = CartService(uow)
    await cart_service.add_product(user_id=1, product_id=1, quantity=2, price=2.00)
    cart = await cart_service.get_cart(user_id=1)

    assert cart is not None
    assert any(item.product_id == 1 for item in cart.items)
    assert cart.items[0].quantity == 2


@pytest.mark.asyncio
async def test_cart_total(uow_fixture):
    uow = uow_fixture
    cart_service = CartService(uow)
    await cart_service.add_product(user_id=1, product_id=2, quantity=3, price=2.00)
    total = await cart_service.get_total(user_id=1)

    assert total > 0
    assert isinstance(total, (int, float))
