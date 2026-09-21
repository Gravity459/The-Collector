# Backend Architecture (FastAPI)

> Whole-system view: root [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

## Module map
```
app/
  main.py            # app factory: CORS, router mount, /health
  core/
    config.py        # Settings (pydantic-settings) from .env
    security.py      # hash_password, verify_password, create_access_token, decode_token
    deps.py          # get_db, get_current_user, require_role
  db/
    base.py          # DeclarativeBase (Base) + shared metadata/mixins
    session.py       # async engine + async_sessionmaker
  models/
    users.py         # User
    houses.py        # House
    collection.py    # Collection
  schemas/           # Pydantic request/response DTOs
  repositories/      # UserRepo, HouseRepo, CollectionRepo (async queries)
  services/          # AuthService, UserService, CollectionService
  api/v1/            # auth.py, users.py, collections.py routers
  utils/pagination.py# Page[T] envelope + paginate() helper
alembic/             # env.py (async) + versions/
tests/
```

## Request lifecycle
1. Router receives request, resolves deps (`get_db`, `get_current_user`, `require_role`).
2. Router validates body/query via Pydantic schema.
3. Router calls a service method.
4. Service applies business rules, calls repositories.
5. Repository runs the SQLAlchemy query against `AsyncSession`.
6. Service returns domain data; router serializes to a response schema.

## Data model
```
User(id uuid pk, name, email unique, password[argon2], role check('user','admin'),
     created_at, updated_at)
House(id uuid pk, house_number int unique, created_at, updated_at)
Collection(id uuid pk, house_id fk->houses.id, amount int, approved bool default false,
           created_at, updated_at)
```
`created_at` default `now()`, `updated_at` on-update `now()` (both timestamptz).

## Core flows
- **Auth**: `/auth/login` verifies argon2, issues JWT. `get_current_user` decodes + loads user. `/auth/me` returns profile.
- **Users**: admin-only `POST /users` (create), `GET /users` (paginated).
- **Collections**:
  - `POST /collections`: `CollectionService` calls `HouseRepo.get_or_create(house_number)`, inserts collection `approved=false`.
  - `PATCH /collections/{id}/approve`: admin-only, sets `approved=true`, bumps `updated_at`.
  - `GET /collections`: role-aware. user → current-month filter + own view; admin → all with `approved`/`house_number` filters. Sorted `created_at desc`, paginated.

## RBAC
`require_role(*roles)` returns a dependency that 403s if `current_user.role` not in `roles`.
Role comes from the DB-loaded user (JWT `sub`), not from client input.

## Seeding
Alembic data migration inserts one admin from `ADMIN_EMAIL` / `ADMIN_PASSWORD` / `ADMIN_NAME`
(hashed at migration time). Idempotent: skips if the email already exists.
