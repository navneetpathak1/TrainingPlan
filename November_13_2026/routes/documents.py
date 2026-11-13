from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import models
from schema import DocumentCreate, DocumentUpdate, DocumentResponse


router = APIRouter()

# get all documents

@router.get("", response_model=list[DocumentResponse], status_code=status.HTTP_200_OK)
async def get_all_documents(db: Annotated[AsyncSession, Depends(get_db)]):
    response = await db.execute(select(models.Documents))

    data = response.scalars().all()

    if not data:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Document is empty")

    return data


# create document

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_document(doc: DocumentCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    new_doc = models.Documents(
        tenant_id=doc.tenant_id,
        source_id=doc.source_id,
        title=doc.title,
        category=doc.category,
        content_hash=doc.content_hash,
        version=doc.version
    )

    db.add(new_doc)

    await db.commit()
    await db.refresh(new_doc)

    return new_doc


# Update document

@router.patch("/{tenant_id}/{source_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def update_documents(tenant_id:str, source_id:str, doc:DocumentUpdate, db:Annotated[AsyncSession, Depends(get_db)]):
    exist = await db.execute(select(models.Documents).where((models.Documents.tenant_id == tenant_id ) & (models.Documents.source_id == source_id)))
    data = exist.scalar_one_or_none()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with Tenant_id: {tenant_id} and source id {source_id} not exist")
    update_data = doc.model_dump(exclude_unset=True)

    if "title" in update_data:
        data.title = update_data["title"]

    if "category" in update_data:
        data.category = update_data["category"]

    if "content_hash" in update_data:
        data.content_hash = update_data["content_hash"]

    if "tenant_id" in update_data:
        data.tenant_id = update_data["tenant_id"]

    if "source_id" in update_data:
        data.source_id = update_data["source_id"]
    

    await db.commit()
    await db.refresh(data)

    return data


# Get document by id

@router.get("/{source_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def update_documents(source_id:str, db:Annotated[AsyncSession, Depends(get_db)]):
    exist = await db.execute(select(models.Documents).where(models.Documents.source_id == source_id))
    data = exist.scalar_one_or_none()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with source id {source_id} not exist")


    return data


# Delete

@router.delete("/{source_id}", status_code=status.HTTP_200_OK)
async def update_documents(source_id:str, db:Annotated[AsyncSession, Depends(get_db)]):
    exist = await db.execute(select(models.Documents).where(models.Documents.source_id == source_id))
    data = exist.scalar_one_or_none()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with source id {source_id} not exist")

    await db.delete(data)
    await db.commit()
    return {"message": "Document deleted successfully"}




@router.get("/import_jobs", status_code=status.HTTP_200_OK)
async def get_import_jobs(db: Annotated[AsyncSession, Depends(get_db)]):
    response = await db.execute(select(models.ImportJobs))
    data = response.scalars().all()

    if not data:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Import jobs is empty")

    return data

