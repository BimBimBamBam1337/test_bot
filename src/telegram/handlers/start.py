from loguru import logger
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from src.database.uow import UnitOfWork
from src.telegram.texts import start_text

router = Router()


@router.message(CommandStart())
async def start(message: types.Message, uow: UnitOfWork):
    """Регистрация пользователя"""
    async with uow:
        user_exist = await uow.users_repo.get_by_field(
            "telegram_id", message.from_user.id
        )  # type:ignore
        if user_exist is None:
            user = await uow.users_repo.create({"telegram_id": message.from_user.id, "name": message.from_user.username})  # type: ignore
            logger.info(f"Registrate user {user.telegram_id}")
    await message.answer(
        text=start_text,
        parse_mode="HTML",
    )
