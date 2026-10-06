# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- **Collector**: walks the housing society door to door, mostly on a phone, logging the cash each house hands over. Needs to record "house + amount" in seconds and see what they logged this month.
- **Admin**: works on a desktop. Reviews collections waiting for approval, approves or rejects them, removes mistaken approved payments, and manages user accounts (create, change password, remove).
- **User (resident)**: read-only, on phone or desktop. Checks that a house's payment for a given month is approved.

## Product Purpose
Track monthly collection amounts per house and move them from "Pending Approval" to "Approved" under admin control. Success: every rupee collected is logged once, approved by an admin, and findable by house and month.

## Positioning
A single-society ledger with a two-step trust model: collectors submit, only admins approve. Residents see only approved money.

## Operating Context
- Houses are identified as `S-<house number>` (e.g. S-14). This format is mandatory everywhere a house appears.
- Amounts are whole numbers in Pakistani rupees, displayed as `PKR 5,000`.
- Monthly cycle: views are scoped to a calendar month; collectors see the current month only.

## Capabilities and Constraints
- Roles: `collector`, `user`, `admin`. RBAC is enforced by the backend; the UI only reflects it.
- Collections: create (collector), approve / reject (admin, pending), remove (admin, approved), list with house/month/approved filters, paginated (10 per page), monthly totals.
- Users: create, change password, remove (admin only; cannot remove self).
- Charts and reports are planned but not built yet.
- Stack: Next.js App Router + Tailwind + TanStack Query front end; FastAPI back end; deployed on Vercel.

## Evidence on Hand
No real customer data, testimonials, or metrics are available in the repo. Do not fabricate any.

## Product Principles
1. Logging a collection must be the fastest action in the product.
2. Pending vs approved must never be ambiguous.
3. The backend is the source of truth; the UI never implies permissions it does not have.
4. Calm and dense over decorative: this is a tool used repeatedly every month.

## Accessibility & Inclusion
Status and role must never be conveyed by colour alone. Touch targets on phone screens at least 44px for collector inputs.
