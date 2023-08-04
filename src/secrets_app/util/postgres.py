import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
from urllib.parse import parse_qs

from fastapi import Request
from pydantic import PostgresDsn as PydanticPostgresDsn
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import text
from sqlmodel import SQLModel


def parse_query_string(value: Optional[str]) -> dict[str, str]:
    if not value:
        return {}
    return {k: str(v[0]) for k, v in parse_qs(value).items()}


async def postgres_session_dependency(request: Request) -> AsyncIterator[AsyncSession]:
    client: PostgresClient = request.app.state.postgres_client
    async with client.session() as ses:
        yield ses


class PostgresDsn(PydanticPostgresDsn):
    def create_sqlalchemy_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=int(self.port or 5432),
            database=self.path.split("/")[-1] if self.path else None,
            query=parse_query_string(self.query),
        )

    def to_string(self) -> str:
        return self.create_sqlalchemy_url().render_as_string(hide_password=False)

    def __str__(self) -> str:
        return self.to_string()


class PostgresClient:
    def __init__(self, dsn: PostgresDsn):
        self._engine = create_async_engine(
            dsn.create_sqlalchemy_url(),
            future=True,
            poolclass=QueuePool,
            pool_pre_ping=True,
        )
        self._session_factory = async_scoped_session(
            session_factory=sessionmaker(
                self._engine,
                autocommit=False,
                expire_on_commit=False,
                class_=AsyncSession,  # type: ignore
            ),
            scopefunc=asyncio.current_task,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            yield session

    async def on_startup(self):
        async with self.session() as session:
            await session.execute(text("SELECT 1"))
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
