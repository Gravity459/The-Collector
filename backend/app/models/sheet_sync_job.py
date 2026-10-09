"""One Google Sheet write per approved collection."""
from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

JOB_STATUSES = ("pending", "done", "needs_review", "failed")
REVIEW_REASONS = (
    "conflict",
    "house_not_in_sheet",
    "month_column_missing",
    "layout_unreadable",
)


class SheetSyncJob(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sheet_sync_jobs"
    __table_args__ = (
        CheckConstraint(
            "status in ('pending', 'done', 'needs_review', 'failed')",
            name="ck_sheet_sync_jobs_status",
        ),
        CheckConstraint(
            "reason is null or reason in ('conflict', 'house_not_in_sheet', "
            "'month_column_missing', 'layout_unreadable')",
            name="ck_sheet_sync_jobs_reason",
        ),
    )

    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("collection.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending", server_default="pending", index=True
    )
    reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
    target_cell: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # what was already in the cell when a conflict stopped the write
    existing_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    collection: Mapped["Collection"] = relationship(  # noqa: F821
        back_populates="sheet_sync_job"
    )
