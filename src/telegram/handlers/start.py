from loguru import logger
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.database.uow import UnitOfWork
from src.telegram.texts import start_text
from src.telegram.states import Registration

router = Router()


@router.message(CommandStart())
async def start_registration(
    message: types.Message, uow: UnitOfWork, state: FSMContext
):
    """Старт регистрации нового пользователя"""
    async with uow:
        user = await uow.users_repo.get_by_field("telegram_id", message.from_user.id)  # type: ignore
        if user is None:
            user = await uow.users_repo.create(
                {
                    "telegram_id": message.from_user.id,
                    "name": message.from_user.first_name or "Пользователь",
                }
            )
            await uow.carts_repo.create({"user_id": user.telegram_id})
            logger.info(f"Registered user {user.telegram_id} and created empty cart")

    await state.set_state(Registration.name)
    await message.answer("Добро пожаловать! Введите ваше имя:")


@router.message(Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Registration.phone)
    await message.answer("Введите ваш телефон (например, +79991234567):")


@router.message(Registration.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if not phone.startswith("+") or len(phone) < 10:
        await message.answer("❌ Некорректный телефон, попробуйте снова:")
        return
    await state.update_data(phone=phone)
    await state.set_state(Registration.address)
    await message.answer("Введите ваш адрес доставки:")


@router.message(Registration.address)
async def process_address(message: types.Message, state: FSMContext, uow: UnitOfWork):
    await state.update_data(address=message.text)
    data = await state.get_data()

    async with uow:
        user = await uow.users_repo.get_by_field("telegram_id", message.from_user.id)
        if user:
            await uow.users_repo.update(
                user.id,
                {
                    "name": data["name"],
                    "phone": data["phone"],
                    "address": data["address"],
                },
            )
            logger.info(f"Updated user {user.telegram_id} with full registration data")

    await message.answer(
        text="Регистрация завершена! Теперь вы можете добавлять товары в корзину. Доступные команды: /cart,/checkout,/order,/catalog",
    )
    await state.clear()
