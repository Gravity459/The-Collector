# The Collector — Working Rules

Monorepo: `backend/` (FastAPI) + `frontend/` (Next.js). Postgres on Supabase.

> Sub-app rules live in [`backend/CLAUDE.md`](backend/CLAUDE.md) and [`frontend/CLAUDE.md`](frontend/CLAUDE.md). This file is the source of truth for cross-cutting rules; the sub-app files narrow to their stack.

## Golden rules
- Async everywhere in the backend (async routes, async SQLAlchemy session, asyncpg).
- Never commit secrets. All config via env → `core/config.py` (backend) / `NEXT_PUBLIC_*` (frontend). Keep `.env.example` current.
- Every schema change = an Alembic migration. Never edit the DB by hand.
- Enforce RBAC at the API boundary with `require_role`; never trust a role sent from the client.
- Search/filter/sort/pagination is GET + query params. Default page size 10.

## Backend conventions
- Layers: `api → services → repositories → models`. Routers stay thin; logic in services.
- Pydantic schemas for all request/response bodies; never return ORM objects directly.
- Passwords: argon2 via `pwdlib`. JWT via `python-jose`, `{sub, role, exp}` claims.
- Timestamps `timestamptz`; current-month filter uses `date_trunc('month', now())` server-side.
- Tests: `pytest -q`. Add/adjust a test with every endpoint change.

## Frontend conventions
- App Router + TypeScript + Tailwind. Server data via TanStack Query.
- JWT in an httpOnly cookie set by a Next route handler; never in localStorage.
- Role-conditional UI reads role from `/auth/me`, but the backend remains the source of truth.
- Status = pill: green Approved, grey Pending Approval.

## Commands
- Backend: `uvicorn app.main:app --reload` · `alembic upgrade head` · `pytest`
- Frontend: `npm run dev` · `npm run build` · `npm run lint`

## Deploy
- Backend → Railway (Dockerfile). Frontend → Vercel. CORS allowlist = Vercel origin only.

## Roles
Two roles only: `user`, `admin`.
- `user`: submits collections, sees own current-month rows.
- `admin`: creates users, approves collections, sees all rows.
