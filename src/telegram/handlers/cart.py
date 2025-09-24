from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.database.uow import UnitOfWork
from src.services import CartService, ProductService
from src.telegram.keyboards import inline
from src.telegram.utils import build_inline_keyboard
from src.telegram.states import Cart

router = Router()


@router.message(Command("cart"))
async def show_cart(message: Message, uow: UnitOfWork):
    cart_service = CartService(uow)
    product_service = ProductService(uow)

    cart = await cart_service.get_cart(message.from_user.id)
    products = await product_service.get_all()

    # Если корзина пустая или нет элементов
    if not cart or len(cart.items) == 0:
        if not products:
            await message.answer("В данный момент нет доступных продуктов")
        else:
            await message.answer(
                "Ваша корзина пуста. Не хотите добавить пару товаров?",
                reply_markup=build_inline_keyboard(products, prefix="add"),
            )
        return

    text = "Ваша корзина:\n"
    for item in cart.items:
        text += f"{item.product.name} — {item.quantity} шт. — {item.price_at_add} ₽\n"
    total = await cart_service.get_total(message.from_user.id)
    text += f"\nИтого: {total} ₽"

    await message.answer(text, reply_markup=inline.build_cart_panel_kb(cart))


@router.callback_query(F.data.startswith("add"))
async def add_product(callback: CallbackQuery, uow: UnitOfWork, state: FSMContext):
    await state.update_data(product_id=int(callback.data.split(":")[1]))
    await callback.message.answer(text=f"Введите кол-во, которое вы хотите заказать")
    await state.set_state(Cart.how_many)


@router.message(Cart.how_many)
async def add_how_many(message: Message, uow: UnitOfWork, state: FSMContext):
    cart_service = CartService(uow)
    product_service = ProductService(uow)
    try:
        quantity = int(message.text)
    except ValueError:
        await message.answer("Введите целое кол-во")
        return
    data = await state.get_data()
    product = await product_service.get_product(data["product_id"])
    try:
        await cart_service.add_product(
            message.from_user.id, data["product_id"], quantity, product.price
        )
        await message.answer(f"Вы успешно добавили {product.name}")
    except Exception:
        return


@router.callback_query(F.data.startswith("increase"))
async def increase_quantity(callback: CallbackQuery, uow: UnitOfWork):
    product_id = int(callback.data.split(":")[1])
    service = CartService(uow)

    cart = await service.get_cart(callback.from_user.id)
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        await callback.message.answer("Товар не найден в корзине")
        return

    await service.update_quantity(callback.from_user.id, product_id, item.quantity + 1)
    await callback.message.answer(
        f"Количество {item.product.name} увеличено до {item.quantity + 1}"
    )


@router.callback_query(F.data.startswith("decrease"))
async def decrease_quantity(callback: CallbackQuery, uow: UnitOfWork):
    product_id = int(callback.data.split(":")[1])
    service = CartService(uow)

    cart = await service.get_cart(callback.from_user.id)
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        await callback.message.answer("Товар не найден в корзине")
        return
    await service.update_quantity(callback.from_user.id, product_id, item.quantity - 1)
    await callback.message.answer(
        f"Количество {item.product.name} уменьшено на {item.quantity-1}"
    )


@router.callback_query(F.data.startswith("remove_item"))
async def remove_item(callback: CallbackQuery, uow: UnitOfWork):
    product_id = int(callback.data.split(":")[1])
    service = CartService(uow)
    await service.remove_product(callback.from_user.id, product_id)
    await callback.message.answer("Товар удалён из корзины")
