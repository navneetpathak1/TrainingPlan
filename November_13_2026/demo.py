
import asyncio

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import models


async def add_data():
    async for db in get_db():
        new_docs = models.Documents(
            tenant_id="tenant_A",
            source_id="data/file_103",
            title="Technical_101",
            category="Technical",
            content_hash="ABS123",
            version=1
        )

        new_docs2 = models.Documents(
            tenant_id="tenant_B",
            source_id="data/file_102",
            title="Technical_102",
            category="Technical",
            content_hash="Axz123",
            version=2
        )

        try:
            db.add_all([new_docs, new_docs2])
            await db.commit()

            print("Both documents inserted successfully!")

        except Exception as err:
            await db.rollback()
            print(f"Error: {err}")


if __name__ == "__main__":
    asyncio.run(add_data())
