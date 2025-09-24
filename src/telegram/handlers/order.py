from loguru import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.database.uow import UnitOfWork
from src.telegram.keyboards import inline
from src.telegram.states import CheckoutStates
from src.telegram.utils import generate_order_number
from src.services import OrderService, CartService, UserService

router = Router()


@router.message(Command("checkout"))
async def start_checkout(message: Message, state: FSMContext, uow: UnitOfWork):
    user_service = UserService(uow)
    user = await user_service.get_user_by_telegram(message.from_user.id)

    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start")
        return

    if not user.name or not user.phone or not user.address:
        await message.answer("Пожалуйста, введите ваши данные. Введите имя:")
        await state.set_state(CheckoutStates.name)
    else:
        await message.answer(
            "Ваши данные уже сохранены, можно выбирать доставку",
            reply_markup=inline.delivery_panel_kb,
        )

        await state.set_state(CheckoutStates.delivery)


@router.message(CheckoutStates.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш телефон (например, +79991234567):")
    await state.set_state(CheckoutStates.phone)


@router.message(CheckoutStates.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text
    if not phone.startswith("+") or len(phone) < 10:
        await message.answer("Некорректный телефон, попробуйте снова:")
        return
    await state.update_data(phone=phone)
    await message.answer("Введите адрес доставки:")
    await state.set_state(CheckoutStates.address)


@router.message(CheckoutStates.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    await message.answer(
        "Выберите способ доставки:", reply_markup=inline.delivery_panel_kb
    )
    await state.set_state(CheckoutStates.delivery)


@router.callback_query(F.data.startswith("delivery"), CheckoutStates.delivery)
async def process_delivery(callback: CallbackQuery, state: FSMContext, uow: UnitOfWork):
    user_service = UserService(uow)
    cart_service = CartService(uow)

    delivery_type = callback.data.split(":")[1]
    order_number = generate_order_number()

    user = await user_service.get_user_by_telegram(callback.from_user.id)
    cart = await cart_service.get_cart(
        callback.from_user.id
    )  # берём корзину пользователя

    if not cart or not cart.items:
        await callback.message.answer(
            "🛒 Ваша корзина пуста! Добавьте товары перед оформлением заказа."
        )
        return

    # строим текст заказа
    items_text = ""
    total = 0
    for item in cart.items:
        items_text += f"{item.product.name} — {item.quantity} шт. — {item.price_at_add * item.quantity} ₽\n"
        total += item.price_at_add * item.quantity

    # проверка данных пользователя
    if not user.name or not user.phone or not user.address:
        user_name = data.get("name", "Не указано")
        user_phone = data.get("phone", "Не указано")
        user_address = data.get("address", "Не указано")
    else:
        user_name = user.name
        user_phone = user.phone
        user_address = user.address

    text = (
        f"✅ Проверьте ваш заказ:\n"
        f"Имя: {user_name}\n"
        f"Телефон: {user_phone}\n"
        f"Адрес: {user_address}\n"
        f"Доставка: {delivery_type}\n\n"
        f"Ваши товары:\n{items_text}\n"
        f"Итого: {total} ₽"
    )

    await state.update_data(delivery=delivery_type, order_number=order_number)
    await callback.message.answer(text, reply_markup=inline.confirm_panel_kb)
    await state.set_state(CheckoutStates.confirmation)


@router.callback_query(F.data == "confirm", CheckoutStates.confirmation)
async def confirm_order(callback: CallbackQuery, state: FSMContext, uow: UnitOfWork):
    data = await state.get_data()
    service = OrderService(uow)
    order = await service.create_order(
        order_number=data["order_number"],
        user_id=callback.from_user.id,
        delivery_method=data["delivery"],
    )

    await callback.message.answer(f"Ваш заказ #{order.order_number} успешно оформлен!")
    await state.clear()


@router.callback_query(F.data == "cancel", CheckoutStates.confirmation)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Заказ отменён.")
    await state.clear()


@router.callback_query(F.data.startswith("checkout"))
async def checkout(callback: CallbackQuery, uow: UnitOfWork, state: FSMContext):
    user_service = UserService(uow)
    cart_service = CartService(uow)

    user = await user_service.get_user_by_telegram(callback.from_user.id)
    cart = await cart_service.get_cart(user.telegram_id)
    if not user or not user.address:
        await callback.message.answer("У вас нет адреса. Пожалуйста, введите его.")
        await state.set_state(CheckoutStates.address)
        return

    if not cart or not cart.items:
        await callback.message.answer("Ваша корзина пуста.")
        return

    await callback.message.answer(
        "Выберите способ доставки", reply_markup=inline.delivery_panel_kb
    )
    await state.set_state(CheckoutStates.delivery)


@router.callback_query(F.data.startswith("delivery"), CheckoutStates.delivery)
async def chosen_delivery(callback: CallbackQuery, uow: UnitOfWork, state: FSMContext):
    user_service = UserService(uow)
    order_service = OrderService(uow)
    user = await user_service.get_user_by_telegram(callback.from_user.id)

    order = await order_service.create_order(
        order_number=generate_order_number(),
        user_id=user.telegram_id,
        delivery_method=callback.data.split(":")[1],
    )
    await callback.message.answer(f"✅ Заказ №{order.order_number} оформлен!")
