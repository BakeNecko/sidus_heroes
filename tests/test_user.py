""" Test User API with DB/REDIS mock """

from unittest import mock

import pytest
from deepdiff import DeepDiff
from fastapi import FastAPI
from httpx import AsyncClient

from internal.db.repositories.user import UserRepository
from internal.models.schemas import OutUserSchema


@pytest.mark.asyncio
async def test_create_user(app: 'FastAPI', client: 'AsyncClient', user_schema_factory):
    user = user_schema_factory(password="12312300")

    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.create.return_value = user

    with app.container.user_repository.override(repository_mock):
        response = await client.post(
            app.url_path_for('auth:register'),
            json=({
                "email": user.email,
                "username": user.username,
                "password": "12312300",
            })
        )

    assert response.status_code == 201
    assert not DeepDiff({"id": user.id, "email": user.email, "username": user.username}, response.json())


@pytest.mark.asyncio
async def test_get_user(auth_client, user_schema_factory, app):
    user = user_schema_factory()
    client = auth_client()
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.get_by_id.return_value = user

    with app.container.user_repository.override(repository_mock):
        response = client.get(app.url_path_for('user:get', _id=1))

    assert response.status_code == 200
    assert not DeepDiff(OutUserSchema(**user.dict()).dict(), response.json())


@pytest.mark.asyncio
async def test_get_me(auth_client, user_schema_factory, app):
    user = user_schema_factory()
    client = auth_client(user)

    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.get_by_id.return_value = user

    with app.container.user_repository.override(repository_mock):
        response = client.get(app.url_path_for('user:get', _id=1))

    assert response.status_code == 200
    assert not DeepDiff({"id": user.id, "email": user.email, "username": user.username}, response.json())


@pytest.mark.asyncio
async def test_update_user(auth_client, user_schema_factory, app):
    user = user_schema_factory()
    update = user_schema_factory(_id=user.id, email=user.email, password=user.password, username="new")

    client = auth_client(user)
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.update_by_id.return_value = update

    with app.container.user_repository.override(repository_mock):
        response = client.patch(app.url_path_for('user:update'), json={"username": "new"})

    assert response.status_code == 200
    assert not DeepDiff({"id": update.id, "email": update.email, "username": update.username}, response.json())


@pytest.mark.asyncio
async def test_delete_user(auth_client, user_schema_factory, app):
    user = user_schema_factory()

    client = auth_client(user)
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.delete_by_id.return_value = True

    with app.container.user_repository.override(repository_mock):
        response = client.delete(app.url_path_for('user:delete'), json={"username": "new"})

    assert response.status_code == 204
