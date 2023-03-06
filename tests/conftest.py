import asyncio
from typing import Callable, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from storage_app.db_config import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite://"

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=StaticPool, echo=True)

async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
async def async_loop():
    asyncio.set_event_loop(asyncio.new_event_loop())
    yield
    asyncio.get_event_loop().close()


# @pytest_asyncio.fixture(scope="session")
# def event_loop(request) -> Generator:
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

@pytest_asyncio.fixture()
async def engine():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture()
async def db_session(engine: AsyncConnection) -> AsyncSession:
    async with async_session() as session:
        yield session
        await session.flush()
        await session.rollback()


@pytest_asyncio.fixture()
async def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture()
async def _app(override_get_db: Callable) -> FastAPI:
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest_asyncio.fixture()
async def async_client(_app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=_app, base_url="http://127.0.0.1:8000/") as ac:
        yield ac
