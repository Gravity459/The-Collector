"""Collection model."""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Collection(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "collection"
    __table_args__ = (
        # one payment per house per month; a month is stored as its 1st day
        UniqueConstraint("house_id", "period_month", name="uq_collection_house_period"),
        CheckConstraint(
            "extract(day from period_month) = 1", name="ck_collection_period_first_day"
        ),
    )

    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("houses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    collector_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    # the month this payment is FOR (may differ from when it was submitted)
    period_month: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        server_default=text("(date_trunc('month', now()))::date"),
    )
    approved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false", index=True
    )

    house: Mapped["House"] = relationship(back_populates="collections")  # noqa: F821
    collector: Mapped["User | None"] = relationship()  # noqa: F821
