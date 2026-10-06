# Frontend — Working Rules (Next.js)

> Inherits the root [`../CLAUDE.md`](../CLAUDE.md). This file narrows to the frontend stack.

## Stack
Next.js (App Router, TypeScript) · Tailwind CSS · TanStack Query · Axios · react-hook-form + zod · Motion (`motion/react-m` + `LazyMotion`) · lucide-react icons.

## Rules
- App Router only. Server Components by default; add `"use client"` only where interactivity/hooks are needed.
- All server data goes through TanStack Query hooks in `lib/` — no ad-hoc `fetch` in components.
- Auth: JWT stored in an **httpOnly cookie** set by a Next route handler (`app/api/auth/*`). Never localStorage.
- `app/dashboard/layout.tsx` guards `/dashboard/*` — redirects to `/login` when no session cookie. No `middleware.ts`: Edge runtime is unsupported in Vercel Services.
- Role drives UI (`user` vs `admin` Overview) but is presentation only; the backend enforces access.
- Forms use react-hook-form + zod schemas. Validate before submit.
- Status is a **pill**: green = Approved, grey = Pending Approval. Use the shared `StatusPill` component.
- Role is a **pill** via `RolePill`: violet admin, sky collector, amber user. Green/grey stay reserved for status.
- Houses are always rendered with `houseLabel()` (`S-<n>`) and amounts with `formatAmount()` (`PKR 5,000`) from `lib/format.ts`. Never inline either format.
- Primitives live in `components/ui/`: `Button`, `Input`/`Select`, `Field`, `Pill`, `Panel`, `SegmentedTabs`, `DataTable`, `Dialog` (native `<dialog>`), `Skeleton`, `EmptyState`, `AnimatedNumber`. Feature pieces live in `components/`: `Sidebar`, `BottomNav`, `StatusPill`, `RolePill`, `Pagination`, `HouseFilter`, `MonthFilter`, `ApproveButton`, `CollectionForm`, `CollectionsTable`.

## Env
- `NEXT_PUBLIC_API_URL` → backend base URL. Keep `.env.local.example` current.

## Commands
```
npm run dev
npm run build
npm run lint
```

## Design
Visual system is documented in [`DESIGN.md`](DESIGN.md); product truth in [`PRODUCT.md`](PRODUCT.md). Invoke the `impeccable` / `frontend-design` skills before non-trivial UI work.
- Colours come only from the token classes in `tailwind.config.ts` (`bg`, `surface`, `fg`, `border`, `success`, `pending`, `danger`, `role-*`), defined for light and dark in `app/globals.css`. No raw zinc/blue/etc.
- `chart-1` is reserved for the upcoming graphs; nothing else uses it.
- Motion conveys state only (selection, rows entering/leaving, dialogs, values changing). Use `m.*` from `motion/react-m` and presets from `lib/motion.ts`; never `motion.*` (LazyMotion is strict).
- `cn()` is plain `clsx`: when a caller must override a primitive's default utility, use the `!` modifier.
- Loading = skeletons, not spinners. Empty states say what will appear and what to do.
- Desktop sidebar is a 64px icon rail that expands over content on hover/keyboard focus; the pin button keeps it open. Pin state lives in the `sidebar-pinned` cookie (`PIN_COOKIE` in `lib/types.ts`) and is read in `app/dashboard/layout.tsx` so the first paint never shifts.
- List queries use `keepPreviousData`; approve/reject/remove are optimistic across lists *and* totals (`applyOptimistic` in `lib/queries.ts`) so rows, counts and KPIs move together.
