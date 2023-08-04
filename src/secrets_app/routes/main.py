from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .secret import router


def create_app() -> FastAPI:
    limiter = Limiter(key_func=get_remote_address, default_limits=["600/minute"])
    app = FastAPI(
        redoc_url=None,
        openapi_url=f"/openapi.json",
        docs_url=f"/docs",
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.include_router(router, prefix="", tags=["main"])
    app.add_middleware(SlowAPIMiddleware)
    return app
