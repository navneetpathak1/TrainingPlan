
from sqlalchemy import ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC, datetime

from database import Base


class Documents(Base):
    __tablename__ = "documents"

    __table_args__ = (
        UniqueConstraint("tenant_id", "source_id", name="uq_tenant_source"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    tenant_id: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    source_id: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    content_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )


class ImportJobs(Base):
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    accepted_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    rejected_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
