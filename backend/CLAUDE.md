# Backend — Working Rules (FastAPI)

> Inherits the root [`../CLAUDE.md`](../CLAUDE.md). This file narrows to the backend stack.

## Stack
Python 3.12 · FastAPI · Uvicorn · SQLAlchemy 2.0 async + asyncpg · Alembic · pydantic-settings · python-jose · pwdlib[argon2] · pytest.

## Layering (strict)
`api/v1` → `services` → `repositories` → `models`.
- **Routers** (`api/v1/`): parse/validate input, call one service, return a schema. No DB or business logic.
- **Services** (`services/`): business rules (house resolve/create, approve, month filter). No FastAPI types.
- **Repositories** (`repositories/`): SQLAlchemy queries only. Return ORM objects.
- **Models** (`models/`): ORM tables only.

## Rules
- Everything async: `async def` routes, `AsyncSession`, `await` all DB calls.
- Config only through `core/config.Settings`. Read env once; never `os.getenv` scattered.
- Passwords hashed with argon2 (`pwdlib`). Never log or return password hashes.
- JWT claims: `{sub: user_id, role, exp}`. Verify signature + expiry in `get_current_user`.
- RBAC via `require_role("admin")` / `require_role("user")` dependencies. Never read role from request body.
- Response models never expose `password`. Use dedicated `schemas/` Pydantic models.
- Pagination envelope: `{items, page, size, total, total_pages}`. Default `size=10`, `page=1`.

## DB / migrations
- Every model change → `alembic revision --autogenerate -m "..."`, review by hand, then `alembic upgrade head`.
- Supabase connection string uses `postgresql+asyncpg://`. Use the direct/session-pooler URL.

## Commands
```
uvicorn app.main:app --reload
alembic revision --autogenerate -m "msg"
alembic upgrade head
pytest -q
```

## Tests
Add/adjust a test with every endpoint change. Cover: auth, RBAC (403 on wrong role), pagination math, current-month boundary, approve flow.
