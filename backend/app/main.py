"""FastAPI application factory."""
from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="The Collector API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/db", tags=["health"])
    async def health_db(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
        # Real DB query; pinged daily by Vercel Cron to keep Supabase free tier awake.
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}

    # Routers (mounted as phases land)
    from app.api.v1 import auth, collections, users

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(collections.router, prefix="/api/v1")

    return app


app = create_app()
