"""User management business logic (admin)."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.users import User
from app.repositories.user_repo import UserRepository
from app.schemas.common import Page, PageParams
from app.schemas.user import UserCreate, UserOut
from app.utils.pagination import build_page


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.users = UserRepository(db)

    async def create_user(self, data: UserCreate) -> UserOut:
        existing = await self.users.get_by_email(data.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
        user = User(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
            role=data.role,
        )
        created = await self.users.create(user)
        return UserOut.model_validate(created)

    async def list_users(self, params: PageParams) -> Page[UserOut]:
        rows, total = await self.users.list(offset=params.offset, limit=params.size)
        items = [UserOut.model_validate(u) for u in rows]
        return build_page(items, total=total, page=params.page, size=params.size)
