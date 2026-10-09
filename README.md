<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-dark.svg">
  <img alt="The Collector: monthly house collections, from doorstep to approved." src="docs/assets/banner-light.svg" width="100%">
</picture>

<br/>

**Log the cash each house pays, approve it, and look it up by house and month.**<br/>
A ledger for a single housing society. Collectors submit payments, admins approve them, and residents only ever see approved money.

<br/>

![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Postgres-Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-38BDF8?style=flat-square&logo=tailwindcss&logoColor=white)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=flat-square&logo=vercel&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-A1A1A1?style=flat-square)](LICENSE)

[**Features**](#-features) · [**Screenshots**](#-screenshots) · [**Quick start**](#-quick-start) · [**Usage**](#-using-the-app) · [**API**](#-api) · [**Deploy**](#-deploy)

</div>

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/showcase/admin-overview-dark.png">
  <img alt="Admin overview: approved total for the month, pending total, and the queue of collections waiting for approval" src="docs/showcase/admin-overview-light.png" width="100%">
</picture>

<br/>

## ✨ Features

|  |  |
| --- | --- |
| 🧾 **Fast logging on a phone** | A collector types a house number and an amount, taps submit, and the row appears in their list. Inputs are sized for touch. |
| ✅ **Two-step approval** | Every submission starts as **Pending approval**. Only an admin can mark it **Approved**, or reject it. |
| 📊 **Monthly totals** | The admin overview shows the month's approved total, the change against last month, and the amount still waiting for approval. |
| 🔎 **Filter by house and month** | Every list can be narrowed to a house (`S-14`) and a calendar month. Results are paginated, 10 per page. |
| 👥 **User management** | Admins create accounts, reset passwords, and remove users (but not themselves). |
| 🔐 **Role-based access, enforced on the server** | `collector`, `user` and `admin` roles are checked by FastAPI on every request. The UI only reflects what the server allows. |
| 🛡️ **One payment per house per month** | Each payment records the month it is **for** (the current month or an earlier one, for arrears). A second payment for the same house and month is refused with `409 Conflict`. |
| 📗 **Google Sheet sync** | Approving a payment writes its amount into your maintenance sheet, in that house's row and that month's column. An AI (Gemini or Grok) reads the sheet's layout, code checks its answer, and anything doubtful waits for the admin. See [Google Sheets sync](#-google-sheets-sync). |
| 🌗 **Light and dark themes** | Follows the system setting, with a manual toggle. Status is always shown with a label as well as a colour. |

## 👤 Roles

| Role | Can do | Sees |
| --- | --- | --- |
| **Admin** | Approve or reject pending collections, remove approved ones, create users, change passwords, remove users | Every collection, any month, with house and status filters |
| **Collector** | Submit collections (stamped with their own ID) | All collections for the **current month** |
| **User** (resident) | Read only | **Approved** payments only, filtered by house and month |

## 📸 Screenshots

> Captured from a local instance seeded with made-up demo data. Images switch to match your GitHub light/dark theme.

### Admin: Overview

The admin's home screen. The KPI strip shows the month's approved total, the change against the previous month, and the amount awaiting approval. Below it, the **Pending** queue has one-click Approve and Reject buttons.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/showcase/admin-approved-dark.png">
  <img alt="Admin overview, Approved tab, filtered to the current month" src="docs/showcase/admin-approved-light.png" width="100%">
</picture>

<table>
  <tr>
    <td width="50%" valign="top">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="docs/showcase/admin-reject-dark.png">
        <img alt="Confirmation dialog before rejecting a pending collection" src="docs/showcase/admin-reject-light.png">
      </picture>
      <p align="center"><sub><b>Reject with confirmation</b>: destructive actions always ask first.</sub></p>
    </td>
    <td width="50%" valign="top">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="docs/showcase/login-dark.png">
        <img alt="Sign-in screen" src="docs/showcase/login-light.png">
      </picture>
      <p align="center"><sub><b>Sign in</b>: accounts are created by an admin; there is no public sign-up.</sub></p>
    </td>
  </tr>
</table>

### Admin: Users

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/showcase/admin-users-dark.png">
  <img alt="Users page listing accounts with role pills and change-password / remove actions" src="docs/showcase/admin-users-light.png" width="100%">
</picture>

<details>
<summary><b>Create-user dialog</b></summary>
<br/>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/showcase/admin-new-user-dark.png">
  <img alt="New user dialog with name, email, password and role fields" src="docs/showcase/admin-new-user-light.png" width="100%">
</picture>
</details>

### Collector and resident on mobile

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/showcase/mobile-dark.png">
    <img alt="Left: collector logging a new collection on a phone. Right: resident viewing approved payments" src="docs/showcase/mobile-light.png" width="720">
  </picture>
  <br/>
  <sub><b>Left:</b> collector logs a payment in seconds. <b>Right:</b> resident checks which payments are approved.</sub>
</p>

## 🧱 Tech stack

| Layer | Tech |
| --- | --- |
| **Frontend** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, TanStack Query, React Hook Form + Zod, Motion, Sonner |
| **Backend** | FastAPI, async SQLAlchemy 2, asyncpg, Alembic, Pydantic v2 |
| **Auth** | JWT (`python-jose`) with `{sub, role, exp}` claims, argon2 hashing (`pwdlib`), token stored in an **httpOnly cookie** |
| **Database** | PostgreSQL on Supabase |
| **Hosting** | Vercel: one project, two Services |

## 🏗️ Architecture

```mermaid
flowchart LR
    B([Browser]) -->|httpOnly JWT cookie| N["Next.js<br/>App Router + route handlers"]
    N -->|"Bearer JWT<br/>(Vercel internal network)"| F["FastAPI<br/>api → services → repositories"]
    F -->|asyncpg| P[(Supabase<br/>Postgres)]
    C{{Vercel Cron<br/>daily}} -.->|/api/cron/keepalive| N
```

- The browser only talks to Next.js. Next.js route handlers (`frontend/app/api/*`) read the JWT from the cookie and forward requests to FastAPI.
- The FastAPI backend is layered: routers stay thin, business rules live in services, and SQL lives in repositories.
- A daily Vercel Cron job calls `/health/db` so the free-tier Supabase project is not paused.

**Data model:**

```
users       (id, name, email!, password, role, created_at, updated_at)
houses      (id, house_number!, created_at, updated_at)
collection  (id, house_id → houses, collector_id → users, amount, approved, created_at, updated_at)
```
<sub>`!` = unique · all primary keys are UUIDs · all timestamps are `timestamptz`</sub>

More detail: [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`backend/ARCHITECTURE.md`](backend/ARCHITECTURE.md) · [`frontend/ARCHITECTURE.md`](frontend/ARCHITECTURE.md) · [`frontend/DESIGN.md`](frontend/DESIGN.md)

## 🚀 Quick start

### Prerequisites

- **Python 3.12+** and [**uv**](https://docs.astral.sh/uv/) (or `pip`)
- **Node.js 18.18+** (20 LTS recommended) and npm
- A **PostgreSQL** database: a [Supabase](https://supabase.com) project, or a local one (see below)

### 1. Clone

```bash
git clone https://github.com/Gravity459/The-Collector.git
```

```bash
cd The-Collector
```

### 2. Backend (FastAPI)

```bash
cd backend
```

```bash
uv sync --extra dev
```

```bash
cp .env.example .env
```

Fill in `.env`:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | Async URL: `postgresql+asyncpg://user:pass@host:5432/db` |
| `JWT_SECRET` | Long random string |
| `JWT_EXPIRE_MINUTES` | Token lifetime (default `1440`) |
| `ADMIN_NAME` / `ADMIN_EMAIL` / `ADMIN_PASSWORD` | The first admin account, created by a data migration |
| `CORS_ORIGINS` | Comma-separated list of allowed origins (`http://localhost:3000` in development) |

Create the schema and the seed admin, then start the API:

```bash
uv run alembic upgrade head
```

```bash
uv run uvicorn app.main:app --reload
```

The API runs at **http://localhost:8000**, with interactive docs at **http://localhost:8000/docs**.

<details>
<summary><b>No Supabase? Use a local Postgres in Docker</b></summary>

```bash
docker run -d --name collector-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=collector -p 5432:5432 postgres:16-alpine
```

Then set:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/collector
```
</details>

### 3. Frontend (Next.js)

```bash
cd frontend
```

```bash
npm install
```

```bash
cp .env.local.example .env.local
```

| Variable | Description |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | FastAPI base URL for local development (`http://localhost:8000`) |
| `CRON_SECRET` | Shared secret Vercel Cron sends to `/api/cron/keepalive` |

```bash
npm run dev
```

Open **http://localhost:3000** and sign in with the `ADMIN_EMAIL` / `ADMIN_PASSWORD` from your backend `.env`.

### 4. Build for production

```bash
npm run build
```

```bash
npm run start
```

The backend has no build step. In production it runs as an ASGI app (`app.main:app`).

## 🧭 Using the app

1. **Sign in as the admin** using the seed credentials.
2. Go to **Users → New user** and create at least one **Collector** account, plus **User** accounts for residents.
3. **Collector:** on a phone, sign in, enter a house number (for example `14`, shown as `S-14`), an amount, and the month it pays for (the current month by default), then tap **Submit collection**. The row shows as **Pending approval**.
4. **Admin:** open **Overview**. The **Pending** tab lists everything awaiting review. Click **Approve**, or **✕** to reject (you will be asked to confirm). Use the **month picker** and **house filter** to narrow the lists. The KPI strip updates as you go. With sheet sync on, approved rows show the sheet cell they were written to, and **Sheet needs attention** lists any that were not.
5. **Resident:** sign in to see **approved** payments only, by month and house.

> [!NOTE]
> Each house can have only **one collection per month paid for**. A duplicate is refused with a clear error message. Month filters and totals go by the month paid for, not the day it was submitted.

## 📗 Google Sheets sync

When an admin approves a payment, the app writes the amount into your Google Sheet, in that house's row (`S-24`) and that month's column (`Amount (Sep 26)`).

**How it works**

1. Approving queues a sheet write, in the same transaction as the approval. The approval is the source of truth, and the sheet is a mirror. A sheet problem never undoes an approval.
2. The backend reads the sheet. An AI (Gemini or Grok) describes its **layout**: header row, house column, month columns, house rows, and the total and summary rows. Names and phone numbers are removed before anything is sent.
3. Code **checks every claim** against the real cells. A layout that fails is retried once with the errors, and is never used if it fails again. The checked layout is saved and reused until the sheet's header row or house column changes, so most approvals make no AI call.
4. The amount is written to the house row × month column. If the month's column doesn't exist yet, it is **added** after the newest month. Total and summary rows are **never written**.
5. If that cell already has anything in it (a number, `HOUSE EMPTY`, `-`), nothing is written. The payment appears under **Sheet needs attention** with an **Overwrite cell** button. Other problems (house not in the sheet, Google unreachable) get **Retry**, and a daily cron retries failures.

**Set it up**

1. In [Google Cloud Console](https://console.cloud.google.com/): create a project, enable the **Google Sheets API**, create a **service account**, and download its JSON key.
2. Open your sheet → **Share** → add the service account's email (`…@….iam.gserviceaccount.com`) as an **Editor**.
3. Get an AI key from [Google AI Studio](https://aistudio.google.com/) (Gemini) or [console.x.ai](https://console.x.ai/) (Grok). A small, fast model is plenty.
4. Set the backend env vars (see [`backend/.env.example`](backend/.env.example)): `GOOGLE_SERVICE_ACCOUNT_JSON` (the key file's contents, or base64 of it), `GOOGLE_SHEET_ID`, `GOOGLE_SHEET_TAB`, `AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`, `CRON_SECRET` (same value as the frontend's), then `SHEET_SYNC_ENABLED=true`.

> [!TIP]
> Try it on a **copy** of your sheet first. When a new month column is added, its total cells are left empty for you to fill with your usual formulas.

## 🔌 API

All routes are under `/api/v1` and require `Authorization: Bearer <JWT>` (except login).

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/login` | public | Exchange email and password for a JWT |
| `GET` | `/auth/me` | any | The current user |
| `POST` | `/collections` | collector | Submit `{house_number, amount, period_month?}` (`YYYY-MM`, defaults to the current month; no future months) |
| `GET` | `/collections` | any | List with `page`, `size`, `house_number`, `approved`, `month=YYYY-MM` (scoped by role) |
| `GET` | `/collections/total` | any | Sum for `approved` + `month` |
| `PATCH` | `/collections/{id}/approve` | admin | Approve a pending collection |
| `DELETE` | `/collections/{id}` | admin | Reject a pending collection or remove an approved one |
| `POST` | `/users` | admin | Create a user |
| `GET` | `/users` | admin | List users (paginated) |
| `PATCH` | `/users/{id}/password` | admin | Change a user's password |
| `DELETE` | `/users/{id}` | admin | Remove a user (not yourself) |
| `POST` | `/collections/{id}/sheet-sync` | admin | Write an approved collection into the Google Sheet now |
| `GET` | `/sheet-sync/jobs` | admin | Sheet writes needing attention (`status` filter, paginated) |
| `POST` | `/sheet-sync/jobs/{id}/overwrite` | admin | Replace a cell that already had a value |
| `POST` | `/sheet-sync/jobs/{id}/retry` | admin | Try a sheet write again |
| `POST` | `/sheet-sync/sweep` | `X-Cron-Secret` | Daily cron: retry pending and failed writes |
| `GET` | `/health`, `/health/db` | public | Liveness checks for the app and the database |

## 🧪 Testing

The backend tests run against a real Postgres database, because they use `gen_random_uuid()` and `date_trunc()`. If `TEST_DATABASE_URL` is not set, they are skipped.

```bash
cd backend
```

```bash
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/collector_test uv run pytest -q
```

Sheet sync tests need no Google or AI account. They use an in-memory copy of an anonymized maintenance sheet ([`tests/fixtures/maintenance_sheet.csv`](backend/tests/fixtures/maintenance_sheet.csv)), and the real Google, Gemini and Grok clients run against a mocked network.

Frontend checks:

```bash
npm run lint
```

## ☁️ Deploy

The app deploys as **one Vercel project with two Services**, defined in [`vercel.json`](vercel.json):

- **`frontend`**: Next.js, serves every public route.
- **`backend`**: FastAPI (`app.main:app`). It is internal only; the frontend reaches it through the `BACKEND_INTERNAL_URL` service binding.

Steps:

1. Set the backend environment variables in Vercel: `DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `ADMIN_*`, and `CORS_ORIGINS` (your Vercel origin only). For sheet sync, also set the variables in [Google Sheets sync](#-google-sheets-sync) and the same `CRON_SECRET` as the frontend.
2. Set `CRON_SECRET` on the frontend.
3. **Back up the database, then run migrations before deploying.** They are not run automatically. Migrations are written to be safe on a live database: the old code keeps working against the new schema.
   ```bash
   uv run alembic upgrade head
   ```
4. Push to the connected branch. Vercel builds both services.
5. Turn sheet sync on last: set `SHEET_SYNC_ENABLED=true` once the app runs fine, then redeploy.

## 📁 Project structure

```
the-collector/
├── backend/                 FastAPI service
│   ├── app/
│   │   ├── api/v1/          routers: auth, users, collections
│   │   ├── services/        business rules
│   │   ├── repositories/    data access
│   │   ├── models/          SQLAlchemy ORM
│   │   ├── schemas/         Pydantic request/response models
│   │   └── core/            config, security, RBAC dependencies
│   ├── alembic/             migrations (schema + seed admin)
│   └── tests/               pytest suite
├── frontend/                Next.js app
│   ├── app/                 App Router pages + /api route handlers (cookie → backend proxy)
│   ├── components/          UI (AdminView, CollectionsTable, UsersView, ui/*)
│   └── lib/                 queries, formatting, motion, server helpers
├── docs/                    README assets (banner, screenshots)
└── vercel.json              two-service Vercel config + cron
```

## 🗺️ Roadmap

- [ ] Charts and monthly reports
- [ ] House management (CRUD)
- [ ] Possible move to Supabase Auth

## 📄 License

[MIT](LICENSE) © 2026 Gravity459
