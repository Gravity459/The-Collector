# Frontend — Working Rules (Next.js)

> Inherits the root [`../CLAUDE.md`](../CLAUDE.md). This file narrows to the frontend stack.

## Stack
Next.js (App Router, TypeScript) · Tailwind CSS · TanStack Query · Axios · react-hook-form + zod.

## Rules
- App Router only. Server Components by default; add `"use client"` only where interactivity/hooks are needed.
- All server data goes through TanStack Query hooks in `lib/` — no ad-hoc `fetch` in components.
- Auth: JWT stored in an **httpOnly cookie** set by a Next route handler (`app/api/auth/*`). Never localStorage.
- `middleware.ts` guards `/dashboard/*` — redirect to `/login` when no valid session cookie.
- Role drives UI (`user` vs `admin` Overview) but is presentation only; the backend enforces access.
- Forms use react-hook-form + zod schemas. Validate before submit.
- Status is a **pill**: green = Approved, grey = Pending Approval. Use the shared `StatusPill` component.
- Reusable pieces live in `components/`: `Sidebar`, `DataTable`, `StatusPill`, `Pagination`, `HouseFilter`, `ApproveButton`, `CollectionForm`.

## Env
- `NEXT_PUBLIC_API_URL` → backend base URL. Keep `.env.local.example` current.

## Commands
```
npm run dev
npm run build
npm run lint
```

## Design
Invoke the `frontend-design` skill before non-trivial UI work. Keep the dashboard clean and consistent; the sidebar is built to hold more entries later (currently just Overview).
