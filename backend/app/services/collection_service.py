"""Collection business logic."""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.collection import Collection
from app.repositories.collection_repo import CollectionRepository, month_start
from app.repositories.house_repo import HouseRepository
from app.repositories.sheet_sync_repo import SheetSyncRepository
from app.schemas.collection import CollectionCreate, CollectionOut, CollectionTotal
from app.schemas.sheet_sync import SheetSyncSummary
from app.schemas.common import Page, PageParams
from app.utils.pagination import build_page


def _to_out(c: Collection) -> CollectionOut:
    job = c.sheet_sync_job
    return CollectionOut(
        id=c.id,
        house_id=c.house_id,
        house_number=c.house.house_number,
        amount=c.amount,
        period_month=c.period_month.strftime("%Y-%m"),
        approved=c.approved,
        collector_name=c.collector.name if c.collector else None,
        sheet_sync=(
            SheetSyncSummary(
                status=job.status,  # type: ignore[arg-type]
                reason=job.reason,  # type: ignore[arg-type]
                target_cell=job.target_cell,
            )
            if job is not None
            else None
        ),
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


class CollectionService:
    def __init__(self, db: AsyncSession) -> None:
        self.collections = CollectionRepository(db)
        self.houses = HouseRepository(db)
        self.sheet_jobs = SheetSyncRepository(db)

    async def submit(
        self, data: CollectionCreate, *, collector_id: uuid.UUID
    ) -> CollectionOut:
        current = await self.collections.current_period()
        period = month_start(data.period_month) if data.period_month else current
        # arrears are fine; advance payments are not
        if period > current:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Payments can't be recorded for a future month.",
            )
        house = await self.houses.get_or_create(data.house_number)
        if await self.collections.exists_for_period(house.id, period):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"A collection for house S-{data.house_number} already exists "
                    f"for {period:%B %Y}."
                ),
            )
        created = await self.collections.create(
            house_id=house.id,
            amount=data.amount,
            collector_id=collector_id,
            period_month=period,
        )
        return _to_out(created)

    async def approve(self, collection_id: uuid.UUID) -> CollectionOut:
        collection = await self.collections.get_by_id(collection_id)
        if collection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
            )
        if collection.approved:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Collection already approved",
            )
        updated = await self.collections.approve(collection)
        if get_settings().sheet_sync_enabled:
            # same transaction: an approval never exists without its sheet job
            await self.sheet_jobs.create_for_collection(updated.id)
            updated = await self.collections.get_by_id(updated.id)  # type: ignore[assignment]
        return _to_out(updated)

    async def delete(self, collection_id: uuid.UUID) -> None:
        collection = await self.collections.get_by_id(collection_id)
        if collection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
            )
        await self.collections.delete(collection)

    async def total(
        self, *, approved: bool = True, month: str | None = None
    ) -> CollectionTotal:
        # approved: one month (default current); pending: all-time, like the list
        total = await self.collections.sum_amount(
            approved=approved, month=month, all_months=not approved
        )
        return CollectionTotal(total=total)

    async def list(
        self,
        params: PageParams,
        *,
        house_number: int | None = None,
        approved: bool | None = None,
        current_month_only: bool = False,
        current_period_only: bool = False,
        month: str | None = None,
    ) -> Page[CollectionOut]:
        rows, total = await self.collections.list(
            offset=params.offset,
            limit=params.size,
            house_number=house_number,
            approved=approved,
            current_month_only=current_month_only,
            current_period_only=current_period_only,
            month=month,
        )
        items = [_to_out(c) for c in rows]
        return build_page(items, total=total, page=params.page, size=params.size)
