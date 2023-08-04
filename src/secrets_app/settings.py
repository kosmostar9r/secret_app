import asyncio
from typing import Awaitable, Callable

from fastapi.datastructures import State
from pydantic import BaseConfig
from pydantic import BaseSettings as PydanticBaseSettings

from .util.postgres import PostgresClient, PostgresDsn


class BaseSettings(PydanticBaseSettings):
    @classmethod
    def read_env(cls):
        return cls()


class AppSettings(BaseSettings):
    postgres_url: PostgresDsn

    class Config(BaseConfig):
        pass

    def on_startup_callback(self, state: "State") -> Callable[[], Awaitable[None]]:
        state.postgres_client = PostgresClient(self.postgres_url)

        async def on_startup() -> None:
            await asyncio.gather(state.postgres_client.on_startup())

        return on_startup
