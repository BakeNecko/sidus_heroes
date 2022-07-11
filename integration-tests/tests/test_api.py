from dataclasses import dataclass

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


@dataclass
class User:
    id: int
    password: str
    email: str
    username: str


def check_user(user: dict, expected: dict):
    if user_id := user.get('id', None):
        assert str(user_id) == str(expected.get('id'))
    assert user.get('username') == expected.get('username')
    assert user.get('email') == expected.get('email')


@pytest.mark.asyncio
async def test_full_user_api(client: 'AsyncClient', app: 'FastAPI'):
    # Register
    data = {
        "email": "test1@email.com",
        "username": "username1",
        "password": "12312300",
    }

    response = await client.post(
        app.url_path_for('auth:register'),
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    check_user(data, response.json())
    user = User(**response.json(), password="12312300")

    # sing-up with same username/email
    response = await client.post(
        app.url_path_for('auth:register'),
        json=data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Login
    response = await client.post(
        app.url_path_for('auth:login'),
        json={
            "username": user.username,
            "password": user.password,
        }
    )
    assert response.status_code == status.HTTP_200_OK
    jwt = response.json().get('token')
    client.headers.update({'Authorization': f'Bearer {jwt}'})

    # Failed login
    response = await client.post(
        app.url_path_for('auth:login'),
        json={
            "username": user.username,
            "password": 'hackerman',
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Get /me
    response = await client.get(app.url_path_for('user:me'))

    assert response.status_code == status.HTTP_200_OK
    check_user({"id": user.id, "email": user.email, "username": user.username}, response.json())

    # Update /me
    user.username = "new_username"
    response = await client.patch(
        app.url_path_for('user:update'),
        json={
            "username": user.username,
        }
    )
    assert response.status_code == status.HTTP_200_OK
    check_user({"id": user.id, "email": user.email, "username": user.username}, response.json())

    # Check info is updated
    response = await client.get(app.url_path_for('user:get', _id=user.id))

    assert response.status_code == status.HTTP_200_OK
    check_user({"id": user.id, "email": user.email, "username": user.username}, response.json())

    # Delete user
    response = await client.delete(app.url_path_for('user:delete'))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check user is deleted
    response = await client.post(
        app.url_path_for('auth:login'),
        json={
            "username": user.username,
            "password": user.password,
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_check_protected_api(client: 'AsyncClient', app: 'FastAPI'):
    endpoints = [
        ('GET', app.url_path_for('user:get', _id=1)),
        ('GET', app.url_path_for('user:me')),
        ('DELETE', app.url_path_for('user:delete')),
        ('PATCH', app.url_path_for('user:update')),
    ]
    for method, endpoint in endpoints:
        response = await client.request(method, endpoint)
        assert response.status_code == 401
