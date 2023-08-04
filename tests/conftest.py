from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from secrets_app.bin.server import WebServerSettings, asgi_app_factory
from secrets_app.util.postgres import PostgresClient

settings = WebServerSettings.read_env()
app = asgi_app_factory()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_app() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(app=app, base_url="https://test") as t_a:
        yield t_a


@pytest.fixture(scope="session")
async def database() -> AsyncGenerator[AsyncSession, Any]:
    client: PostgresClient = PostgresClient(settings.postgres_url)
    async with client.session() as session:
        yield session
