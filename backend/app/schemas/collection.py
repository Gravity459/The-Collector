"""Collection schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"  # YYYY-MM


class CollectionCreate(BaseModel):
    house_number: int = Field(gt=0)
    amount: int = Field(gt=0)
    # month the payment is for; omitted -> current month (resolved server-side)
    period_month: str | None = Field(default=None, pattern=MONTH_PATTERN)


class CollectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    house_id: uuid.UUID
    house_number: int
    amount: int
    period_month: str  # YYYY-MM
    approved: bool
    collector_name: str | None = None
    created_at: datetime
    updated_at: datetime


class CollectionTotal(BaseModel):
    total: int
