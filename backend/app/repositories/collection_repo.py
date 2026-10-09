"""Collection data access."""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.collection import Collection
from app.models.houses import House


_LOAD = (
    joinedload(Collection.house),
    joinedload(Collection.collector),
    joinedload(Collection.sheet_sync_job),
)


def month_start(month: str) -> date:
    """Convert "YYYY-MM" to the first day of that month."""
    year, mon = month.split("-")
    return date(int(year), int(mon), 1)


def _current_period():
    """First day of the current month, computed server-side."""
    return cast(func.date_trunc("month", func.now()), Date)


def _in_month(month: str):
    """Rows paid for `month` ("YYYY-MM")."""
    return Collection.period_month == month_start(month)


class CollectionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, collection_id: uuid.UUID) -> Collection | None:
        result = await self.db.execute(
            select(Collection)
            .options(*_LOAD)
            .where(Collection.id == collection_id)
            # re-read relationships (e.g. a sync job added after the first load)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def current_period(self) -> date:
        return await self.db.scalar(select(_current_period()))  # type: ignore[return-value]

    async def exists_for_period(self, house_id: uuid.UUID, period_month: date) -> bool:
        result = await self.db.scalar(
            select(func.count())
            .select_from(Collection)
            .where(Collection.house_id == house_id)
            .where(Collection.period_month == period_month)
        )
        return bool(result)

    async def sum_amount(
        self,
        *,
        approved: bool,
        month: str | None = None,
        all_months: bool = False,
    ) -> int:
        stmt = select(func.coalesce(func.sum(Collection.amount), 0)).where(
            Collection.approved.is_(approved)
        )
        if month is not None:
            stmt = stmt.where(_in_month(month))
        elif not all_months:
            stmt = stmt.where(Collection.period_month == _current_period())
        result = await self.db.scalar(stmt)
        return int(result or 0)

    async def create(
        self,
        *,
        house_id: uuid.UUID,
        amount: int,
        collector_id: uuid.UUID,
        period_month: date,
    ) -> Collection:
        collection = Collection(
            house_id=house_id,
            amount=amount,
            collector_id=collector_id,
            period_month=period_month,
            approved=False,
        )
        self.db.add(collection)
        await self.db.flush()
        # reload with house relationship for serialization
        return await self.get_by_id(collection.id)  # type: ignore[return-value]

    async def approve(self, collection: Collection) -> Collection:
        collection.approved = True
        collection.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(collection)
        return collection

    async def delete(self, collection: Collection) -> None:
        await self.db.delete(collection)
        await self.db.flush()

    async def list(
        self,
        *,
        offset: int,
        limit: int,
        house_number: int | None = None,
        approved: bool | None = None,
        current_month_only: bool = False,
        current_period_only: bool = False,
        month: str | None = None,
    ) -> tuple[list[Collection], int]:
        base = select(Collection).join(House, Collection.house_id == House.id)

        if house_number is not None:
            base = base.where(House.house_number == house_number)
        if approved is not None:
            base = base.where(Collection.approved == approved)
        if current_month_only:
            # collectors: what was submitted this month, whatever month it pays for
            base = base.where(
                Collection.created_at >= func.date_trunc("month", func.now())
            )
        if current_period_only:
            base = base.where(Collection.period_month == _current_period())
        if month is not None:
            base = base.where(_in_month(month))

        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        ) or 0

        result = await self.db.execute(
            base.options(*_LOAD)
            .order_by(House.house_number.asc(), Collection.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total
