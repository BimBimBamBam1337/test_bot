import pytest
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.database.uow import UnitOfWork
from src.database.models import Base

load_dotenv()


@pytest.fixture(scope="session")
async def uow():
    dsn = os.getenv("DATABASE_DSN")
    if not dsn:
        raise RuntimeError("DATABASE_DSN not found in .env")

    engine = create_async_engine(dsn, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    uow = UnitOfWork(session_factory)
    yield uow

    # удаляем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
