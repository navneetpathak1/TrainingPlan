
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DocumentBase(BaseModel):
    tenant_id: str
    source_id: str
    title: str
    category: str
    content_hash: str


class DocumentCreate(DocumentBase):
    version: str | None = 1
    pass


class DocumentUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    content_hash: str | None = None
    tenant_id: str | None = None
    source_id: str | None = None

class DocumentResponse(DocumentBase):
    id: int
    version: int
    created_at: datetime
    source_id: str

    model_config = ConfigDict(from_attributes=True)


class ImportJobBase(BaseModel):
    status: str
    accepted_count: int = 0
    rejected_count: int = 0


class ImportJobCreate(ImportJobBase):
    pass


class ImportJobResponse(ImportJobBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
