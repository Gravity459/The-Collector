"""House data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.houses import House


class HouseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_number(self, house_number: int) -> House | None:
        result = await self.db.execute(
            select(House).where(House.house_number == house_number)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, house_number: int) -> House:
        house = await self.get_by_number(house_number)
        if house is not None:
            return house
        house = House(house_number=house_number)
        self.db.add(house)
        await self.db.flush()
        await self.db.refresh(house)
        return house
