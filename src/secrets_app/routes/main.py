from fastapi import FastAPI


def create_app(root_path: str) -> FastAPI:
    app = FastAPI(
        redoc_url=None,
        openapi_url=f"{root_path}/openapi.json",
        docs_url=f"{root_path}/docs",
    )
    return app
