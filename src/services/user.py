from src.database.uow import UnitOfWork
from src.database.models import User


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.uow as uow:
            return await uow.users_repo.get(user_id)

    async def get_user_by_telegram(self, telegram_id: int) -> User | None:
        async with self.uow as uow:
            return await uow.users_repo.get_by_field("telegram_id", telegram_id)

    async def update_user(self, user_id: int, data: dict) -> User | None:
        async with self.uow as uow:
            return await uow.users_repo.update(user_id, data)

    async def delete_user(self, user_id: int):
        async with self.uow as uow:
            await uow.users_repo.delete(user_id)

    async def get_all_users(self) -> list[User]:
        async with self.uow as uow:
            return await uow.users_repo.get_all()
