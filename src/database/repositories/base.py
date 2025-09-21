from typing import TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from src.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get(self, obj_id: int) -> ModelType | None:
        result = await self.session.get(self.model, obj_id)
        return result

    async def get_by_field(self, field_name: str, value) -> ModelType | None:
        stmt = select(self.model).where(getattr(self.model, field_name) == value)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> list[ModelType]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def update(self, obj_id: int, obj_in: dict) -> ModelType | None:
        await self.session.execute(
            update(self.model).where(self.model.id == obj_id).values(**obj_in)
        )
        await self.session.flush()
        return await self.get(obj_id)

    async def delete(self, obj_id: int) -> None:
        await self.session.execute(delete(self.model).where(self.model.id == obj_id))
        await self.session.flush()
