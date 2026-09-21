"""Pytest fixtures.

Tests need a real Postgres database (they exercise gen_random_uuid() and
date_trunc()). Set TEST_DATABASE_URL to an async URL, e.g.:

    postgresql+asyncpg://postgres:postgres@localhost:5432/collector_test

If TEST_DATABASE_URL is not set, the suite is skipped.
"""
from __future__ import annotations

import os

import pytest

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

# Configure required settings before app modules import.
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL or "postgresql+asyncpg://x")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")
os.environ.setdefault("ADMIN_NAME", "Admin")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.local")
os.environ.setdefault("ADMIN_PASSWORD", "admin-pass-123")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL, reason="TEST_DATABASE_URL not set"
)

if TEST_DATABASE_URL:
    import httpx
    from httpx import ASGITransport
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.core.security import hash_password
    from app.db.base import Base
    from app.db.session import get_db
    from app.main import app
    from app.models.users import User

    engine = create_async_engine(TEST_DATABASE_URL, poolclass=None)
    TestSession = async_sessionmaker(engine, expire_on_commit=False)

    @pytest.fixture(autouse=True)
    async def _schema():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest.fixture
    async def db_session():
        async with TestSession() as session:
            yield session

    @pytest.fixture(autouse=True)
    def _override_db():
        async def _get_db_override():
            async with TestSession() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

        app.dependency_overrides[get_db] = _get_db_override
        yield
        app.dependency_overrides.clear()

    @pytest.fixture
    async def seeded_admin(db_session):
        admin = User(
            name="Admin",
            email="admin@test.local",
            password=hash_password("admin-pass-123"),
            role="admin",
        )
        db_session.add(admin)
        await db_session.commit()
        return admin

    @pytest.fixture
    async def client():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as ac:
            yield ac

    @pytest.fixture
    async def admin_token(client, seeded_admin):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.local", "password": "admin-pass-123"},
        )
        assert resp.status_code == 200
        return resp.json()["access_token"]
