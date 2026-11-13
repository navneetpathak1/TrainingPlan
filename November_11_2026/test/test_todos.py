import pytest
from httpx import AsyncClient

from test.conftest import create_test_user


@pytest.mark.anyio
async def test_get_todo_not_found(client: AsyncClient):
    response = await client.get("/todos")

    assert response.status_code == 404
    assert response.json()["detail"] == "No todo found"


@pytest.mark.anyio
async def test_create_post_success(client: AsyncClient):
    user = await create_test_user(client)

    response = await client.post(
        f"/todos/{user["id"]}",
        json={
            "title": "My First Post",
            "content": "This is the content"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "My First Post"
    assert data["content"] == "This is the content"
    assert data["user_id"] == user["id"]
    assert "id" in data
    