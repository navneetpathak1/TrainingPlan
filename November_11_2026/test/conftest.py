import os
from collections.abc import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()


os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL")

os.environ["SECRET_KEY"] = "TEST_SECRET_KEY"



import boto3
import pytest
from httpx import ASGITransport, AsyncClient
from moto import mock_aws
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database import Base, get_db
from main import app

pytest_plugins = ["anyio"]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool, #can cause error 
    )
    return engine

