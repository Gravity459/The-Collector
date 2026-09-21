"""Authentication business logic."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.models.users import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.users = UserRepository(db)

    async def authenticate(self, *, email: str, password: str) -> TokenResponse:
        user: User | None = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        token = create_access_token(subject=user.id, role=user.role)
        return TokenResponse(access_token=token)
