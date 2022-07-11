from fastapi import FastAPI

from internal.app.api.api import api_v1_router
from internal.app.container import Container


def create_app() -> FastAPI:
    # Dependencies Injection
    container = Container()
    settings = container.settings()

    # Apps
    application = FastAPI(
        title=settings.APP_CONFIG.TITLE,
        version=settings.APP_CONFIG.VERSION,
    )
    application.container = container

    # Routers
    prefix = '/api/v1'
    application.include_router(api_v1_router, prefix=prefix)

    return application
