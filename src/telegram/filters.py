from aiogram.filters import BaseFilter
from aiogram.types import Message
from src.database.uow import UnitOfWork


class AdminFilter(BaseFilter):

    async def __call__(self, message: Message, uow: UnitOfWork) -> bool:
        async with uow:
            user = await uow.users_repo.get_by_field(
                "telegram_id", message.from_user.id
            )
            return user.is_admin
