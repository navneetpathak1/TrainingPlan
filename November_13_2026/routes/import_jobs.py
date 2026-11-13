
import csv
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
import models

router = APIRouter()

CSV_FILE = Path(
    r"C:\js\genAI\Training_plan\November_13_2026\cleaned_file.csv"
)


@router.get("/jobs", status_code=status.HTTP_200_OK)
async def get_all_documents(db: Annotated[AsyncSession, Depends(get_db)]):
    response = await db.execute(select(models.ImportJobs))

    data = response.scalars().all()

    if not data:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Jobs is empty")

    return data 



@router.post("/import-cleaned-file")
async def import_cleaned_file(
    db: Annotated[AsyncSession, Depends(get_db)]
):

    with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)
        rows = list(reader)

        if not rows:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty"
            )

    # Get existing tenant_id and source_id combinations
    result = await db.execute(
        select(
            models.Documents.tenant_id,
            models.Documents.source_id
        )
    )

    existing_records = set(result.all())

    inserted_count = 0
    skipped_count = 0

    try:
        # Import all document rows
        for row in rows:

            key = (row["tenant_id"], row["source_id"])

            # Skip duplicate records
            if key in existing_records:
                skipped_count += 1
                continue

            document = models.Documents(
                tenant_id=row["tenant_id"],
                source_id=row["source_id"],
                title=row["title"],
                category=row["category"],
                content_hash=row["content_hash"]
            )

            db.add(document)

            # Track inserted key to prevent CSV duplicates
            existing_records.add(key)
            inserted_count += 1

        # Take import job values from first CSV data row
        first_row = rows[0]

        import_job = models.ImportJobs(
            status=first_row["status"],
            accepted_count=int(first_row["accepted_count"]),
            rejected_count=int(first_row["rejected_count"]),
        )

        db.add(import_job)

        await db.commit()
        await db.refresh(import_job)

        return {
            "message": "CSV imported successfully",
            "import_job_id": import_job.id,
            "status": import_job.status,
            "accepted_count": import_job.accepted_count,
            "rejected_count": import_job.rejected_count,
            "inserted_documents": inserted_count,
            "skipped_documents": skipped_count
        }

    except Exception:
        await db.rollback()
        raise
