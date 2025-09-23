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
from src.services import OrderService

router = Router()


@router.message(Command("checkout"))
async def start_checkout(message: Message, state: FSMContext):
    await message.answer("📝 Введите ваше имя:")
    await state.set_state(CheckoutStates.name)


@router.message(CheckoutStates.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📞 Введите ваш телефон (например, +79991234567):")
    await state.set_state(CheckoutStates.phone)


@router.message(CheckoutStates.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text
    if not phone.startswith("+") or len(phone) < 10:
        await message.answer("❌ Некорректный телефон, попробуйте снова:")
        return
    await state.update_data(phone=phone)
    await message.answer("🏠 Введите адрес доставки:")
    await state.set_state(CheckoutStates.address)


@router.message(CheckoutStates.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    await message.answer(
        "Выберите способ доставки:", reply_markup=inline.delivery_panel_kb
    )
    await state.set_state(CheckoutStates.delivery)


@router.callback_query(F.data.startswith("delivery:"), CheckoutStates.delivery)
async def process_delivery(callback: CallbackQuery, state: FSMContext):
    delivery_type = callback.data.split(":")[1]
    order_number = generate_order_number()
    await state.update_data(delivery=delivery_type, order_number=order_number)
    data = await state.get_data()
    text = (
        f"✅ Проверьте ваш заказ:\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"Доставка: {data['delivery']}\n"
        f"Сумма: 0 ₽ (потом можно посчитать из корзины)"
    )

    await callback.message.answer(text, reply_markup=inline.confirm_panel_kb)
    await state.set_state(CheckoutStates.confirmation)


@router.callback_query(F.data == "confirm_order", CheckoutStates.confirmation)
async def confirm_order(callback: CallbackQuery, state: FSMContext, uow: UnitOfWork):
    data = await state.get_data()
    service = OrderService(uow)
    order = await service.create_order(
        order_number=data["order_number"],
        user_id=callback.from_user.id,
        contact_info={
            "name": data["name"],
            "phone": data["phone"],
            "address": data["address"],
            "delivery": data["delivery"],
        },
    )

    await callback.message.answer(
        f"🎉 Ваш заказ #{order.order_number} успешно оформлен!"
    )
    await state.clear()


@router.callback_query(F.data == "cancel_order", CheckoutStates.confirmation)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Заказ отменён.")
    await state.clear()
