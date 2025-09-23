from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.filters import Command
from src.database.uow import UnitOfWork
from src.services import CartService, ProductService
from src.telegram.keyboards import inline
from src.telegram.utils import build_inline_keyboard

router = Router()


@router.message(Command("cart"))
async def show_cart(message: Message, uow: UnitOfWork):
    cart_service = CartService(uow)
    product_service = ProductService(uow)
    cart = await cart_service.get_cart(message.from_user.id)
    products = await product_service.get_all()

    if not cart or not cart.items:
        if products is None:
            await message.answer(
                text="В данный момент нет доспутных продуктов",
            )
            return
        else:
            await message.answer(
                text="🛒 Ваша корзина пуста. Не хотите добавить пару товаров?",
                reply_markup=build_inline_keyboard(products, "add"),
            )
    else:
        text = "🛒 Ваша корзина:\n"
        for item in cart.items:
            text += (
                f"{item.product.name} — {item.quantity} шт. — {item.price_at_add} ₽\n"
            )
        text += f"\nИтого: {await cart_service.get_total(message.from_user.id)} ₽"

        await message.answer(text, reply_markup=inline.build_cart_kb(cart))


@router.callback_query(F.data.startswith("add"))
async def add_product(callback: CallbackQuery, uow: UnitOfWork):
    await callback.message.answer(text=f'{callback.data.split(":")[1]}')


@router.callback_query(F.data.startswith("update_qty"))
async def update_quantity(callback: CallbackQuery, uow: UnitOfWork):
    product_id = int(callback.data.split(":")[1])
    service = CartService(uow)

    cart = await service.get_cart(callback.from_user.id)
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        await callback.message.answer("❌ Товар не найден в корзине")
        return

    await service.update_quantity(callback.from_user.id, product_id, item.quantity + 1)
    await callback.message.answer(
        f"✅ Количество {item.product.name} увеличено до {item.quantity + 1}"
    )


@router.callback_query(F.data.startswith("remove_item"))
async def remove_item(callback: CallbackQuery, uow: UnitOfWork):
    product_id = int(callback.data.split(":")[1])
    service = CartService(uow)
    await service.remove_product(callback.from_user.id, product_id)
    await callback.message.answer("❌ Товар удалён из корзины")
