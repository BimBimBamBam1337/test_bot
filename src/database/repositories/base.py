from typing import TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from src.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, session: AsyncSession, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get(self, session: AsyncSession, obj_id: int) -> ModelType | None:
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalars().first()

    async def get_all(self, session: AsyncSession) -> list[ModelType]:
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    async def update(
        self, session: AsyncSession, obj_id: int, obj_in: dict
    ) -> ModelType | None:
        await session.execute(
            update(self.model).where(self.model.id == obj_id).values(**obj_in)
        )
        await session.commit()
        return await self.get(session, obj_id)

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        await session.execute(delete(self.model).where(self.model.id == obj_id))
        await session.flush()
