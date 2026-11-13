from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from test.conftest import create_test_user


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/users",
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 422
    assert "password" in response.text


    
@pytest.mark.anyio
async def test_create_user(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/users",
        json={
            "username": "different_user",
            "password": "password123",
        },
    )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_create_user_duplicate_username(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "password": "password123",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == 'Not Found'

