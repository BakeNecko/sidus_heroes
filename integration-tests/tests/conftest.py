import sys
sys.path.append("..")

import pytest

from fastapi import FastAPI
from httpx import AsyncClient

from internal.app.app import create_app


@pytest.fixture
async def app() -> 'FastAPI':
    app = create_app()
    await app.container.db().init_db()
    return app


@pytest.fixture
async def client(app: 'FastAPI') -> 'AsyncClient':
    async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"}
    ) as client:
        yield client
