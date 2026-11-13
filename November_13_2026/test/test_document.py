import pytest
from httpx import AsyncClient

try:
    from test.conftest import create_test_document
except ImportError:
    from conftest import create_test_document



#  create
@pytest.mark.anyio
async def test_create_document(client: AsyncClient):
    response = await client.post(
        "/documents",
        json={
            "tenant_id": "tenant_A",
            "source_id": "doc_001",
            "title": "Initial Document",
            "category": "General",
            "content_hash": "abc123hash"
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["tenant_id"] == "tenant_A"
    assert data["source_id"] == "doc_001"
    assert data["title"] == "Initial Document"
    assert "id" in data


# find pass

@pytest.mark.anyio
async def test_get_documents(client: AsyncClient):
    await create_test_document(client, tenant_id="tenant_B", source_id="doc_002")

    response = await client.get("/documents")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# find fail


@pytest.mark.anyio
async def test_get_fail(client: AsyncClient):
    await create_test_document(client, tenant_id="tenant_B", source_id="doc_002")

    response = await client.get("/xyz")

    assert response.status_code == 404


# update  pass
@pytest.mark.anyio
async def test_update_document(client: AsyncClient):
    doc = await create_test_document(
        client,
        tenant_id="tenant_C",
        source_id="doc_003",
        title="Old Title",
    )

    response = await client.patch(
        f"/documents/{doc['tenant_id']}/{doc['source_id']}",
        json={"title": "Updated Title"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"

# update fail

@pytest.mark.anyio
async def test_update_fail(client: AsyncClient):
    doc = await create_test_document(
        client,
        tenant_id="tenant_C",
        source_id="doc_003",
        title="Old Title",
    )

    response = await client.patch(
        "/documents/abd/abd",
        json={"title": "Updated Title"},
    )

    assert response.status_code == 404


# delete

@pytest.mark.anyio
async def test_delete_document(client: AsyncClient):
    doc = await create_test_document(
        client,
        tenant_id="tenant_D",
        source_id="doc_004",
    )

    response = await client.delete(f"/documents/{doc['source_id']}")

    assert response.status_code == 200
    assert response.json() == {"message": "Document deleted successfully"}


# wrong url
@pytest.mark.anyio
async def test_delete_fail(client: AsyncClient):
    doc = await create_test_document(
        client,
        tenant_id="tenant_D",
        source_id="doc_004",
    )

    response = await client.delete("/documents/random")

    assert response.status_code == 404
    assert response.json() == {
    "success": False,
    "message": "Document with source id random not exist",
    "path": "http://test/documents/random"
}


