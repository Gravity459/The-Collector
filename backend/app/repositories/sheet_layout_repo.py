"""Sheet Layout Map data access."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sheet_layout import SheetLayout


class SheetLayoutRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_latest(self, spreadsheet_id: str, tab_name: str) -> SheetLayout | None:
        result = await self.db.execute(
            select(SheetLayout)
            .where(SheetLayout.spreadsheet_id == spreadsheet_id)
            .where(SheetLayout.tab_name == tab_name)
            .order_by(SheetLayout.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save(
        self,
        *,
        spreadsheet_id: str,
        tab_name: str,
        fingerprint: str,
        layout: dict[str, Any],
        source: str,
    ) -> SheetLayout:
        row = SheetLayout(
            spreadsheet_id=spreadsheet_id,
            tab_name=tab_name,
            fingerprint=fingerprint,
            layout=layout,
            source=source,
        )
        self.db.add(row)
        await self.db.flush()
        return row
