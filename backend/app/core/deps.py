"""Shared FastAPI dependencies: DB session, current user, RBAC."""
from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import JWTError, decode_token
from app.db.session import get_db
from app.models.users import User
from app.repositories.user_repo import UserRepository

bearer_scheme = HTTPBearer(auto_error=True)

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise _CREDENTIALS_ERROR
        user_id = uuid.UUID(str(subject))
    except (JWTError, ValueError):
        raise _CREDENTIALS_ERROR

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise _CREDENTIALS_ERROR
    return user


def require_role(*roles: str) -> Callable[[User], Awaitable[User]]:
    """Dependency factory: 403 unless the current user's role is allowed."""

    async def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _checker
