from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import models
from schema import DocumentCreate, DocumentUpdate, DocumentResponse


router = APIRouter()


# get all data

@router.get("", response_model=list[DocumentResponse], status_code=status.HTTP_200_OK)
async def get_all_dota(db: Annotated[AsyncSession, Depends(get_db)]):
    response = await db.execute(select(models.ImportJobs))

    data = response.scalars().all()

    if not data:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Jobs is empty")

    return data




