"""Collection business logic."""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.repositories.collection_repo import CollectionRepository
from app.repositories.house_repo import HouseRepository
from app.schemas.collection import CollectionCreate, CollectionOut
from app.schemas.common import Page, PageParams
from app.utils.pagination import build_page


def _to_out(c: Collection) -> CollectionOut:
    return CollectionOut(
        id=c.id,
        house_id=c.house_id,
        house_number=c.house.house_number,
        amount=c.amount,
        approved=c.approved,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


class CollectionService:
    def __init__(self, db: AsyncSession) -> None:
        self.collections = CollectionRepository(db)
        self.houses = HouseRepository(db)

    async def submit(self, data: CollectionCreate) -> CollectionOut:
        house = await self.houses.get_or_create(data.house_number)
        if await self.collections.exists_current_month(house.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"A collection for house S-{data.house_number} already exists "
                    "for this month."
                ),
            )
        created = await self.collections.create(house_id=house.id, amount=data.amount)
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
        return _to_out(updated)

    async def delete(self, collection_id: uuid.UUID) -> None:
        collection = await self.collections.get_by_id(collection_id)
        if collection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
            )
        await self.collections.delete(collection)

    async def list(
        self,
        params: PageParams,
        *,
        house_number: int | None = None,
        approved: bool | None = None,
        current_month_only: bool = False,
    ) -> Page[CollectionOut]:
        rows, total = await self.collections.list(
            offset=params.offset,
            limit=params.size,
            house_number=house_number,
            approved=approved,
            current_month_only=current_month_only,
        )
        items = [_to_out(c) for c in rows]
        return build_page(items, total=total, page=params.page, size=params.size)
