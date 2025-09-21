class ProductService:
    def __init__(self, uow):
        self.uow = uow

    async def list_products(self):
        async with self.uow as uow:
            return await uow.products.list()

    async def get_product(self, product_id: int):
        async with self.uow as uow:
            return await uow.products.get(product_id)

    async def add_product(
        self, name: str, description: str, price: float, stock: int, photo_url: str
    ):
        async with self.uow as uow:
            return await uow.products.add(
                name=name,
                description=description,
                price=price,
                stock=stock,
                photo_url=photo_url,
            )

    async def update_product(self, product_id: int, data: dict):
        async with self.uow as uow:
            product = await uow.products.get(product_id)
            for key, value in data.items():
                setattr(product, key, value)
            await uow.session.commit()
            return product
