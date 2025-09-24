from src.database.uow import UnitOfWork
from src.database.models import Category


class CategoryService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def list_categories(self):
        async with self.uow as uow:
            return await uow.categories_repo.get_all()

    async def get_category(self, category_id: int) -> Category | None:
        async with self.uow as uow:
            return await uow.categories_repo.get(category_id)
