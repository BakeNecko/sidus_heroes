from typing import AsyncIterator, Callable, Iterator

import pytest
from asgi_lifespan import LifespanManager
from dependency_injector import providers
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.testclient import TestClient

from internal.app.api.dependencies import get_current_user
from internal.app.app import create_app
from internal.app.container import Container
from internal.db.tables.user import User
from internal.models.schemas import UserSchema
from internal.pkg.cache import Cache


class CacheMock(Cache):
    def __init__(self, cache=None, *args, **kwargs):
        if cache is None:
            cache = dict()
        self.cache = cache
        super(CacheMock, self).__init__(*args, **kwargs)

    async def ping(self) -> bool:
        return True

    async def set(self, key: str, value: any, expires: float) -> bool:
        self.cache[key] = value
        return True

    async def get(self, key: str) -> any:
        return self.cache.get(key, None)

    async def flash_all(self) -> bool:
        self.cache.clear()
        return True

    async def remove_key(self, key: str) -> bool:
        return bool(self.cache.pop(key, None))


class OverridingContainer(Container):
    cache = providers.Singleton(CacheMock)


@pytest.fixture
def faker() -> 'Faker':
    Faker.seed(0)
    f = Faker()
    return f


@pytest.fixture
def app() -> 'FastAPI':
    app = create_app()

    overriding_container = OverridingContainer()
    app.container.override(overriding_container)

    return app


@pytest.fixture
async def client(app: 'FastAPI') -> 'AsyncClient':
    # INFO: httpx не реализует протокол lifespan и не запускает ивенты start/shutdown (у ASGI).
    # LifespanManager позволяет это обойти. т.е срабатывает триггер @app.on_event("startup/shutdown") у app.
    # Т.к я использую фабрику приложений create_app() мне он тут, по правде говоря не нужен....
    # async with LifespanManager(app):
    async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"}
    ) as client:
        yield client


@pytest.fixture
def auth_client(app: 'FastAPI', user_schema_factory) -> Callable[..., 'Iterator["TestClient"]']:
    def _client(user=user_schema_factory()) -> Iterator['TestClient']:
        async def _get_current_user():
            return user

        app.dependency_overrides[get_current_user] = _get_current_user
        client = TestClient(
            app=app,
            base_url="http://testserver",
        )
        return client

    return _client


@pytest.fixture
def user_table_factory(faker: 'Faker') -> Callable[..., 'User']:
    def _make_user_table(
            _id: int = faker.pyint(),
            password: str = faker.password(12),
            username: str = faker.user_name(),
            email: str = faker.email(),
    ):
        return User(
            id=_id,
            password=password,
            username=username,
            email=email
        )

    return _make_user_table


@pytest.fixture
def user_schema_factory(faker: 'Faker', user_table_factory) -> Callable[..., 'UserSchema']:
    def _make_user_schema(
            _id: int = faker.pyint(),
            password: str = faker.password(12),
            username: str = faker.user_name(),
            email: str = faker.email(),
    ):
        user = user_table_factory(_id, password, username, email)
        return UserSchema.from_orm(user)

    return _make_user_schema
