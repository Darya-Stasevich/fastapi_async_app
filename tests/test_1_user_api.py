import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def test_create_user(async_client: AsyncClient, db_session: AsyncSession):
    response = await async_client.post("/users/", json={'username': 'dasha@mail.ru', 'password': '12345'})
    assert response.status_code == 201


async def test_get_users(async_client: AsyncClient, db_session: AsyncSession):
    await async_client.post("/users/", json={'username': 'dasha@mail.ru', 'password': '12345'})
    await async_client.post("/users/", json={'username': 'dasha2@mail.ru', 'password': '12345'})
    response = await async_client.get("/users/")
    print(response.json())
    assert response.status_code == 200
