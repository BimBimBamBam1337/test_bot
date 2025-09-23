from src.database.uow import UnitOfWork


class ProductService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all(self):
        async with self.uow as uow:
            return await uow.products_repo.get_all()

    async def get_product(self, product_id: int):
        async with self.uow as uow:
            return await uow.products_repo.get(product_id)

    async def add_product(
        self, name: str, description: str, price: float, stock: int, photo_url: str
    ):
        async with self.uow as uow:
            return await uow.products_repo.add(
                name=name,
                description=description,
                price=price,
                stock=stock,
                photo_url=photo_url,
            )

    async def update_product(self, product_id: int, data: dict):
        async with self.uow as uow:
            product = await uow.products_repo.get(product_id)
            for key, value in data.items():
                setattr(product, key, value)
            await uow.session.commit()
            return product
