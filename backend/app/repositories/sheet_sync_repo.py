"""Sheet sync job data access."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.collection import Collection
from app.models.sheet_sync_job import SheetSyncJob

_WITH_COLLECTION = joinedload(SheetSyncJob.collection).joinedload(Collection.house)


class SheetSyncRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_for_collection(self, collection_id: uuid.UUID) -> SheetSyncJob:
        job = SheetSyncJob(collection_id=collection_id, status="pending", attempts=0)
        self.db.add(job)
        await self.db.flush()
        return job

    async def get(self, job_id: uuid.UUID) -> SheetSyncJob | None:
        result = await self.db.execute(
            select(SheetSyncJob)
            .options(_WITH_COLLECTION)
            .where(SheetSyncJob.id == job_id)
            # a job just updated in this session must be re-read, not served stale
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def get_by_collection(self, collection_id: uuid.UUID) -> SheetSyncJob | None:
        result = await self.db.execute(
            select(SheetSyncJob)
            .options(_WITH_COLLECTION)
            .where(SheetSyncJob.collection_id == collection_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, *, statuses: Sequence[str], offset: int, limit: int
    ) -> tuple[list[SheetSyncJob], int]:
        base = select(SheetSyncJob).where(SheetSyncJob.status.in_(statuses))
        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        ) or 0
        result = await self.db.execute(
            base.options(_WITH_COLLECTION)
            .order_by(SheetSyncJob.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def list_retryable_ids(self, *, max_attempts: int) -> list[uuid.UUID]:
        """Pending jobs, plus failed ones that still have attempts left; oldest first."""
        result = await self.db.execute(
            select(SheetSyncJob.id)
            .where(
                or_(
                    SheetSyncJob.status == "pending",
                    (SheetSyncJob.status == "failed")
                    & (SheetSyncJob.attempts < max_attempts),
                )
            )
            .order_by(SheetSyncJob.created_at.asc())
        )
        return list(result.scalars().all())
