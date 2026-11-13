import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from dotenv import load_dotenv

# Ensure November_13_2026 directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv()

# Set test database URL
test_db_url = os.getenv("TEST_DATABASE_URL")

os.environ["DATABASE_URL"] = test_db_url

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database import Base, get_db
from main import app

pytest_plugins = ["anyio"]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine():
    db_url = os.environ.get("DATABASE_URL")
    engine = None
    if db_url:
        try:
            eng = create_async_engine(db_url, poolclass=NullPool)
            async with eng.connect():
                pass
            engine = eng
        except Exception:
            # Fallback to local SQLite if remote/PostgreSQL connection fails
            engine = create_async_engine("sqlite+aiosqlite:///./test.db", poolclass=NullPool)
    else:
        engine = create_async_engine("sqlite+aiosqlite:///./test.db", poolclass=NullPool)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()


@pytest.fixture
async def client(
    db_session: AsyncSession
) -> AsyncGenerator[AsyncClient]:

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_test_document(
    client: AsyncClient,
    tenant_id: str = "tenant_B",
    source_id: str = "file_102",
    title: str = "Technical_102",
    category: str = "Technical",
    content_hash: str = "Axz123"
) -> dict:
    response = await client.post(
        "/documents",
        json={
            "tenant_id": tenant_id,
            "source_id": source_id,
            "title": title,
            "category": category,
            "content_hash": content_hash
        },
    )

    assert response.status_code == 201, (
        f"Failed to create document: {response.text}"
    )

    return response.json()
