"""Collection routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.users import User
from app.schemas.collection import CollectionCreate, CollectionOut, CollectionTotal
from app.schemas.common import Page, PageParams
from app.services.collection_service import CollectionService

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("", response_model=CollectionOut, status_code=status.HTTP_201_CREATED)
async def submit_collection(
    payload: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("user")),
) -> CollectionOut:
    return await CollectionService(db).submit(payload)


@router.get("", response_model=Page[CollectionOut])
async def list_collections(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    house_number: int | None = Query(default=None, gt=0),
    approved: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[CollectionOut]:
    params = PageParams(page=page, size=size)
    service = CollectionService(db)

    if current_user.role == "admin":
        # admins see everything; `approved` filter drives the two dashboard sections
        return await service.list(
            params, house_number=house_number, approved=approved
        )

    # regular users: current month only
    return await service.list(
        params, house_number=house_number, current_month_only=True
    )


@router.get("/total", response_model=CollectionTotal)
async def current_month_total(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> CollectionTotal:
    return await CollectionService(db).current_month_total()


@router.patch("/{collection_id}/approve", response_model=CollectionOut)
async def approve_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> CollectionOut:
    return await CollectionService(db).approve(collection_id)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> None:
    await CollectionService(db).delete(collection_id)
