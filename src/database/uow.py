from sqlalchemy.ext.asyncio import AsyncSession
from .repositories import *


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.categories_repo = CategoryRepository(self.session)
        self.products_repo = ProductRepository(self.session)
        self.users_repo = UserRepository(self.session)
        self.carts_repo = CartRepository(self.session)
        self.orders_repo = OrderRepository(self.session)
        self.order_items_repo = OrderItemRepository(self.session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
