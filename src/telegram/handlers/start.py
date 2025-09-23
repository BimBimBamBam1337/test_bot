from loguru import logger
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from src.database.uow import UnitOfWork
from src.telegram.texts import start_text
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(CommandStart())
async def start(message: types.Message, uow: UnitOfWork, state: FSMContext):
    """Регистрация пользователя"""
    async with uow:
        user = await uow.users_repo.get_by_field(
            "telegram_id", message.from_user.id
        )  # type:ignore
        if user is None:
            user = await uow.users_repo.create(
                {
                    "telegram_id": message.from_user.id,
                    "name": message.from_user.username,
                    "phone": message.from_user.phone,
                }
            )
            await uow.carts_repo.create({"user_id": user.telegram_id})
            logger.info(f"Registered user {user.telegram_id} and created empty cart")

    await state.clear()
    await message.answer(
        text=start_text,
        parse_mode="HTML",
    )
