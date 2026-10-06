---
version: 1
slug: "app-dashboard-overview-page-tsx"
primary_target: "app/dashboard/overview/page.tsx"
related_targets: ["app/dashboard/users/page.tsx","app/(auth)/login/page.tsx"]
---

Scope: dashboard surfaces (overview per role, users, login). Visitor mode: Operate.
Audience/job: admin approves pending collections on desktop; collector logs S-<n> + PKR amount on a phone; resident verifies approved payments.

## Direction contract
THESIS: A quiet ledger for a housing society's monthly dues where pending money visibly becomes approved money; refuses the stock SaaS KPI-card grid and centred tables.
OWN-WORLD: Near-black #0A0A0A ground (light #FAFAFA), hairline #262626 bordered panels, Geist with tabular figures, white primary button, no brand accent. Colour only for jobs: green Approved, grey Pending, violet admin, sky collector, amber user, red danger.
STORY: Admin sees what's waiting, approves, watches it land in the month's Approved total. Collector logs S-14 · PKR 5,000 in seconds. Resident confirms their payment is approved.
FIRST VIEWPORT: Admin desktop: 232px sidebar; header row with Overview title, month stepper, S- filter; two KPI panels (Approved in month with delta vs last month; Awaiting approval); one panel with Pending|Approved segmented tabs over a dense left-aligned table, amounts right-aligned. Collector phone: inline S-/PKR entry form on top, This month list below as stacked rows, bottom tab nav.
FORM: Pinned by user (Hybrid Resend/Supabase). No seed key. Signature move: the approval hand-off — approved row collapses out of Pending while Pending count ticks down and Approved count + KPI tick up.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
