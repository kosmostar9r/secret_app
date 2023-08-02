from pathlib import Path

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field, PositiveInt
from uvicorn.config import LoopSetupType

from secrets_app.routes import create_app
from secrets_app.settings import AppSettings


class RunSettings(BaseModel):
    host = "localhost"
    port: PositiveInt = 8080
    root_path: str = ""
    event_loop: LoopSetupType = "uvloop"
    reload: bool = False
    workers: int = 1


class WebServerSettings(AppSettings):
    run: RunSettings = Field(default_factory=RunSettings)


settings = WebServerSettings.read_env()


def asgi_app_factory() -> "FastAPI":
    app = create_app(settings.run.root_path)
    app.add_event_handler(
        "startup", settings.on_startup_callback(app.state)  # type:ignore
    )
    app.add_api_route(
        "/health", health_endpoint, include_in_schema=False  # type:ignore
    )
    return app


async def health_endpoint():
    return {}


def get_asgi_app_factory_str() -> str:
    path = Path(__file__)
    module = ".".join((*path.parent.parts[-2:], path.stem))
    return f"{module}:{asgi_app_factory.__name__}"


# packages = [{include = "secrets_app", from = "src"}]


def main():
    uvicorn.run(
        get_asgi_app_factory_str(),
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
        loop=settings.run.event_loop,
        workers=settings.run.workers,
        factory=True,
    )


if __name__ == "__main__":
    main()
