"""Sheet sync schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

JobStatus = Literal["pending", "done", "needs_review", "failed"]
ReviewReason = Literal[
    "conflict", "house_not_in_sheet", "month_column_missing", "layout_unreadable"
]


class SheetSyncSummary(BaseModel):
    """Sync state shown next to an approved collection."""

    status: JobStatus
    reason: ReviewReason | None = None
    target_cell: str | None = None


class SheetSyncJobOut(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID
    house_number: int
    period_month: str  # YYYY-MM
    amount: int
    status: JobStatus
    reason: ReviewReason | None = None
    target_cell: str | None = None
    existing_value: str | None = None
    error: str | None = None
    attempts: int
    updated_at: datetime


class SweepResult(BaseModel):
    processed: int
    done: int
    needs_review: int
    failed: int
