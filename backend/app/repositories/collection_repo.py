"""Collection data access."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.collection import Collection
from app.models.houses import House


class CollectionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, collection_id: uuid.UUID) -> Collection | None:
        result = await self.db.execute(
            select(Collection)
            .options(joinedload(Collection.house))
            .where(Collection.id == collection_id)
        )
        return result.scalar_one_or_none()

    async def exists_current_month(self, house_id: uuid.UUID) -> bool:
        result = await self.db.scalar(
            select(func.count())
            .select_from(Collection)
            .where(Collection.house_id == house_id)
            .where(Collection.created_at >= func.date_trunc("month", func.now()))
        )
        return bool(result)

    async def create(self, *, house_id: uuid.UUID, amount: int) -> Collection:
        collection = Collection(house_id=house_id, amount=amount, approved=False)
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
    ) -> tuple[list[Collection], int]:
        base = select(Collection).join(House, Collection.house_id == House.id)

        if house_number is not None:
            base = base.where(House.house_number == house_number)
        if approved is not None:
            base = base.where(Collection.approved == approved)
        if current_month_only:
            base = base.where(
                Collection.created_at >= func.date_trunc("month", func.now())
            )

        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        ) or 0

        result = await self.db.execute(
            base.options(joinedload(Collection.house))
            .order_by(Collection.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total
