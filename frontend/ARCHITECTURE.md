# Frontend Architecture (Next.js)

> Whole-system view: root [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

## Route/module map
```
app/
  (auth)/login/page.tsx        # login form
  api/auth/login/route.ts      # proxies backend login, sets httpOnly cookie
  api/auth/logout/route.ts     # clears cookie
  dashboard/
    layout.tsx                 # sidebar shell + cookie guard (redirects to /login)
    overview/page.tsx          # role-conditional Overview
  layout.tsx                   # root layout + QueryClient provider
components/
  Sidebar.tsx  DataTable.tsx  StatusPill.tsx  Pagination.tsx
  HouseFilter.tsx  ApproveButton.tsx  CollectionForm.tsx
lib/
  api.ts                       # axios instance (baseURL, auth header)
  auth.ts                      # session/cookie helpers, useMe()
  queries.ts                   # TanStack Query hooks (collections, users)
  types.ts                     # shared TS types (mirror backend schemas)
```

## Auth flow
1. `login/page.tsx` posts credentials to `app/api/auth/login/route.ts`.
2. The route handler calls the backend `/auth/login`, receives JWT, sets it as an httpOnly cookie.
3. `app/dashboard/layout.tsx` checks the cookie; redirects to `/login` if missing.
4. Client hooks read the current user via `/auth/me` to branch the UI on role.

## Data fetching
- `lib/api.ts` — one Axios instance; attaches the JWT (from cookie via route handlers / server calls).
- `lib/queries.ts` — TanStack Query hooks:
  - `useCollections({ page, size, house_number, approved })`
  - `useCreateCollection()`, `useApproveCollection()` (invalidate collection queries on success)
  - `useMe()`
- Pagination consumes the backend envelope `{items, page, size, total, total_pages}`.

## Overview rendering
- **user**: `CollectionForm` + `DataTable` of current-month rows with `StatusPill`; `HouseFilter` + `Pagination`.
- **admin**: two `DataTable` sections —
  - *For Approval* (`approved=false`) with `ApproveButton` per row.
  - *Approved Payments* (`approved=true`).
  Both with `HouseFilter` + `Pagination`. Approve triggers query invalidation so rows move between sections.

## Sheet sync
- `useApproveCollection` fires `POST /api/collections/{id}/sheet-sync` after a successful approve when the response carries `sheet_sync`. It doesn't block, and errors are swallowed because the review panel shows them. Then it invalidates `collections` + `sheet-sync`.
- `SheetSyncBadge` (admin approved list, "Sheet" column): icon + words in neutral ink (`Cell N7`, `Syncing`). `danger` marks `Needs review`/`Sync failed`. It is never a pill, because pills and green/grey belong to payment status.
- `SheetSyncReview` renders above the collections panel only when `useSheetSyncJobs` has items. Each row has a plain-language reason. Conflicts get **Overwrite cell** (via `ConfirmModal`); everything else gets **Retry**.
- `app/api/cron/sheet-sync/route.ts`: the Vercel Cron target. It checks `CRON_SECRET` and forwards to the backend sweep with `X-Cron-Secret`.

## Status pill
`StatusPill` renders a pill: green (`approved`) / grey (`pending`). Single source of truth for status styling.

## Deployment
Vercel Service. Backend URL comes from `BACKEND_INTERNAL_URL` (service binding); `NEXT_PUBLIC_API_URL` is the local-dev fallback.
