"""Collection schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CollectionCreate(BaseModel):
    house_number: int = Field(gt=0)
    amount: int = Field(gt=0)


class CollectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    house_id: uuid.UUID
    house_number: int
    amount: int
    approved: bool
    created_at: datetime
    updated_at: datetime
