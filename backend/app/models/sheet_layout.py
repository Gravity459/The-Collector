"""Saved Layout Map of the Google Sheet (append-only; newest row is current)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDMixin

LAYOUT_SOURCES = ("ai", "code")


class SheetLayout(UUIDMixin, Base):
    __tablename__ = "sheet_layouts"
    __table_args__ = (
        CheckConstraint("source in ('ai', 'code')", name="ck_sheet_layouts_source"),
        Index(
            "ix_sheet_layouts_lookup",
            "spreadsheet_id",
            "tab_name",
            "created_at",
        ),
    )

    spreadsheet_id: Mapped[str] = mapped_column(String(128), nullable=False)
    tab_name: Mapped[str] = mapped_column(String(128), nullable=False)
    # sha256 of the header row + house column; changes when the structure does
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    layout: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source: Mapped[str] = mapped_column(String(8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
