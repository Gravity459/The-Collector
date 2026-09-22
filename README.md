# The Collector

Amount-collection app. Authenticated **users** submit collection amounts against a house;
**admins** approve them and records persist.

- **Backend**: FastAPI + async SQLAlchemy + Alembic on Supabase Postgres → Vercel (Service). See [`backend/`](backend/).
- **Frontend**: Next.js (App Router) + Tailwind + TanStack Query → Vercel. See [`frontend/`](frontend/).

## Docs
- [`CLAUDE.md`](CLAUDE.md) — working rules (monorepo).
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system architecture.
- Sub-app rules & design: [`backend/CLAUDE.md`](backend/CLAUDE.md), [`backend/ARCHITECTURE.md`](backend/ARCHITECTURE.md), [`frontend/CLAUDE.md`](frontend/CLAUDE.md), [`frontend/ARCHITECTURE.md`](frontend/ARCHITECTURE.md).

## Roles
`user` — submit collections, see own current-month rows.
`admin` — create users, approve collections, see all rows.

## Quick start
```bash
# backend
cd backend
cp .env.example .env      # fill Supabase + JWT + admin creds
alembic upgrade head
uvicorn app.main:app --reload

# frontend
cd frontend
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL
npm install
npm run dev
```
