"""Shared FastAPI dependencies: DB session, current user, RBAC."""
from __future__ import annotations

import secrets
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable

import httpx
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import JWTError, decode_token
from app.db.session import get_db
from app.integrations.ai.planner import get_planner
from app.integrations.google_sheets import GoogleSheetsClient
from app.models.users import User
from app.repositories.user_repo import UserRepository
from app.services.sheet_sync_service import SheetSyncService

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


async def require_cron_secret(x_cron_secret: str | None = Header(default=None)) -> None:
    """Guard for cron-only endpoints: X-Cron-Secret must match CRON_SECRET."""
    expected = get_settings().cron_secret
    if not expected or not x_cron_secret or not secrets.compare_digest(
        x_cron_secret, expected
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """One async HTTP client per request, closed when the request ends.

    Per request rather than per process: serverless instances may run each
    request on a fresh event loop, and a pooled client must not outlive its loop.
    """
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0)) as client:
        yield client


def get_sheet_sync_service(
    db: AsyncSession = Depends(get_db),
    http: httpx.AsyncClient = Depends(get_http_client),
) -> SheetSyncService:
    settings = get_settings()
    return SheetSyncService(
        db,
        sheets=GoogleSheetsClient(http, settings),
        planner=get_planner(settings, http),
        settings=settings,
    )
