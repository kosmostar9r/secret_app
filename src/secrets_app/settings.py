from typing import Self
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic import BaseConfig as PydanticBaseConfig


class BaseConfig(PydanticBaseConfig):
    env_prefix = "APP"
    env_nested_delimiter = "__"
    env_file = ".env"


class BaseSettings(PydanticBaseSettings):
    @classmethod
    def read_env(cls) -> "Self":
        return cls()


class AppSettings(BaseSettings):
    ...

    class Config(BaseConfig):
        pass

    def on_startup_callback(self):
        ...
