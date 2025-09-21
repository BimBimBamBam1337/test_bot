from aiogram.filters import BaseFilter
from aiogram.types import Message
from src.database.uow import UnitOfWork


class AdminFilter(BaseFilter):

    async def __call__(self, message: Message, uow: UnitOfWork) -> bool:
        async with uow:
            user = uow.users_repo.get(message.from_user.id)
            return user.is_admin
