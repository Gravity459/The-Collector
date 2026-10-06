---
name: The Collector
description: A quiet monthly ledger where pending money visibly becomes approved money.
colors:
  ground: "#0A0A0A"
  surface: "#0F0F0F"
  surface-raised: "#1C1C1C"
  hairline: "#262626"
  hairline-strong: "#333333"
  ink: "#EDEDED"
  ink-muted: "#A1A1A1"
  ink-subtle: "#8A8A8A"
  on-ink: "#0A0A0A"
  approved: "#4ADE80"
  approved-bg: "#0E2A1C"
  pending: "#A1A1A1"
  pending-bg: "#1C1C1C"
  danger: "#F87171"
  danger-bg: "#2A0F0F"
  role-admin: "#C4B5FD"
  role-admin-bg: "#2A2140"
  role-collector: "#7DD3FC"
  role-collector-bg: "#0C2A3A"
  role-user: "#FCD34D"
  role-user-bg: "#2E2208"
  chart-1: "#7C8CFF"
  ground-light: "#FAFAFA"
  surface-light: "#FFFFFF"
  surface-raised-light: "#F4F4F5"
  hairline-light: "#E4E4E7"
  hairline-strong-light: "#D4D4D8"
  ink-light: "#0A0A0A"
  ink-muted-light: "#52525B"
  ink-subtle-light: "#71717A"
  on-ink-light: "#FFFFFF"
  approved-light: "#15803D"
  approved-bg-light: "#DCFCE7"
  pending-light: "#52525B"
  pending-bg-light: "#F4F4F5"
  danger-light: "#DC2626"
  danger-bg-light: "#FEE2E2"
  role-admin-light: "#6D28D9"
  role-admin-bg-light: "#EDE9FE"
  role-collector-light: "#0369A1"
  role-collector-bg-light: "#E0F2FE"
  role-user-light: "#B45309"
  role-user-bg-light: "#FEF3C7"
  chart-1-light: "#4F5BD5"
typography:
  kpi:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 600
    lineHeight: "2.125rem"
    letterSpacing: "-0.025em"
    fontFeature: "\"tnum\" 1, \"cv11\" 1"
  headline:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: "1.75rem"
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 500
    lineHeight: "1.5rem"
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: "1.375rem"
    fontFeature: "\"tnum\" 1, \"cv11\" 1"
  body-dense:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: "1.25rem"
    fontFeature: "\"tnum\" 1, \"cv11\" 1"
  label:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: "1rem"
rounded:
  control: "6px"
  panel: "8px"
  dialog: "12px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  2xl: "24px"
  3xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    typography: "{typography.body-dense}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "36px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body-dense}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "36px"
  button-secondary-hover:
    backgroundColor: "{colors.surface-raised}"
  button-ghost:
    textColor: "{colors.ink-muted}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "36px"
  button-ghost-hover:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.ink}"
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.ground}"
    typography: "{typography.body-dense}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "36px"
  button-sm:
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 10px"
    height: "28px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body-dense}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "36px"
  input-touch:
    typography: "{typography.title}"
    height: "44px"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
  panel-header:
    padding: "12px 16px"
  kpi-cell:
    padding: "16px 20px"
  pill-approved:
    backgroundColor: "{colors.approved-bg}"
    textColor: "{colors.approved}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: "0 10px"
    height: "22px"
  pill-pending:
    backgroundColor: "{colors.pending-bg}"
    textColor: "{colors.pending}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: "0 10px"
    height: "22px"
  pill-role-admin:
    backgroundColor: "{colors.role-admin-bg}"
    textColor: "{colors.role-admin}"
    rounded: "{rounded.full}"
    height: "22px"
  pill-role-collector:
    backgroundColor: "{colors.role-collector-bg}"
    textColor: "{colors.role-collector}"
    rounded: "{rounded.full}"
    height: "22px"
  pill-role-user:
    backgroundColor: "{colors.role-user-bg}"
    textColor: "{colors.role-user}"
    rounded: "{rounded.full}"
    height: "22px"
  segmented-tabs:
    backgroundColor: "{colors.ground}"
    rounded: "{rounded.control}"
    height: "32px"
  segmented-thumb:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.ink}"
  table-header:
    textColor: "{colors.ink-subtle}"
    typography: "{typography.label}"
    padding: "0 16px"
    height: "36px"
  table-row:
    typography: "{typography.body-dense}"
    padding: "0 16px"
    height: "40px"
  dialog:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.dialog}"
    padding: "24px"
    width: "448px"
  sidebar:
    backgroundColor: "{colors.surface}"
    width: "64px"
  sidebar-expanded:
    width: "232px"
  bottom-nav:
    textColor: "{colors.ink-subtle}"
    typography: "{typography.label}"
    height: "56px"
---

# Design System: The Collector

## Overview

**Creative North Star: "The Quiet Ledger"**

The Collector is a monochrome ledger for a housing society's monthly dues. Everything is ink on a near-black ground (light theme: ink on near-white), drawn in hairlines, set in Geist with tabular figures so every column of rupees lines up. There is no brand accent. Colour appears only when it has a job: a payment's status, a person's role, a destructive action. The absence of colour is the brand; when green shows up, it means money has been approved.

Density is deliberate. Rows are 40px, body copy is 13-14px, panels sit edge to edge with 16px between them, and the KPI strip is one bordered panel split by a hairline rather than a grid of floating cards. The page reads like a ruled book: a title, a toolbar, a strip of two totals, and the queue.

Motion exists to show state changing, never to decorate. The system's signature is the approval hand-off: an approved row slides out of the Pending queue, the remaining rows glide up, the Pending count ticks down, and the month's Approved total ticks up. Every motion preset in the build serves that kind of change (selection, rows entering or leaving, dialogs, numbers moving, views switching).

**Key Characteristics:**
- Monochrome ink-on-ground with no brand accent; both themes driven by the same RGB-triplet tokens.
- Hairline-bordered panels as the single container; tonal steps instead of shadows at rest.
- Geist throughout, tabular figures on by default, houses always `S-<n>`, amounts always `PKR 5,000`.
- Colour reserved for jobs: status, role, destruction.
- Dense, left-anchored tables that become stacked rows on phones.
- Motion that only reports state change, with exponential ease-out and faster exits than entrances.

## Colors

A neutral ink-and-ground scale carries the interface; six small semantic families (approved, pending, danger, three roles) carry meaning, and nothing else is coloured. Every value exists in a dark and a light form; dark is the world's lead rendering, light (the `-light` keys) mirrors it role for role.

### Primary
- **Ledger Ink** (`ink` / `ink-light`): body text, titles, KPI figures, and the fill of the primary button. In light mode the primary button is black; in dark mode it is near-white. It is the closest thing the system has to an accent, and it is spent once per view.
- **On-Ink** (`on-ink` / `on-ink-light`): text on an ink fill (primary button, skip link).

### Neutral
- **Night Ground** (`ground` / `ground-light`): the page itself, the phone top bar and bottom nav (at 85-90% with backdrop blur), and the well of the segmented tabs.
- **Panel Surface** (`surface` / `surface-light`): panels, inputs, secondary buttons, the sidebar, dialogs, toasts.
- **Raised Surface** (`surface-raised` / `surface-raised-light`): hover and selected fills (active nav item, segmented thumb, ghost hover, table header at 50%, row hover at 40%), avatar discs, count chips, skeleton blocks.
- **Hairline** (`hairline` / `hairline-light`): every panel border and divider, table row rules, the sidebar edge.
- **Strong Hairline** (`hairline-strong` / `hairline-strong-light`): control borders (inputs, secondary buttons, month stepper), the segmented thumb's inset edge, scrollbar thumbs, the sheet grab handle.
- **Muted Ink** (`ink-muted` / `ink-muted-light`): descriptions, secondary cells (collector name, relative time), field labels, KPI labels and delta lines.
- **Subtle Ink** (`ink-subtle` / `ink-subtle-light`): table headers, placeholders, input prefixes (`S-`, `PKR`), the KPI currency mark, inactive bottom-nav items, hints.

### Status, role and danger
- **Approved Green** (`approved` on `approved-bg`): the Approved status pill and the success toast icon. Nothing else.
- **Pending Grey** (`pending` on `pending-bg`): the Pending approval pill. It is deliberately the same value as Muted Ink on Raised Surface: pending money has not earned colour yet.
- **Danger Red** (`danger` on `danger-bg`): the confirm button in destructive dialogs, the hover state of Reject and Remove icon buttons, field error text and invalid-input borders, the error toast icon.
- **Admin Violet**, **Collector Sky**, **User Amber** (`role-*` on `role-*-bg`): the role pill only (user table, sidebar account block).
- **Chart Indigo** (`chart-1`): reserved for the planned charts. No component uses it today.

### Named Rules
**The Colour-Has-A-Job Rule.** Every coloured pixel is a status, a role or a destructive action. There is no brand accent, no decorative tint, no raw Tailwind palette; components use only the token classes.

**The Green Means Approved Rule.** Green is reserved for Approved and grey for Pending. Nothing else may borrow either, including trend indicators: the month-over-month delta is written in neutral ink, with direction carried by an arrow and a sign.

**The Never-Colour-Alone Rule.** Every pill pairs its tint with a dot and a text label; colour is never the only carrier of status or role.

**The Reserved Indigo Rule.** `chart-1` belongs to future charts. Do not spend it on UI chrome.

## Typography

**Display Font:** none (the system has no display face)
**Body Font:** Geist (via `next/font`, with ui-sans-serif, system-ui, sans-serif)

**Character:** One neutral grotesk at every level, with tabular figures (`tnum`) and the `cv11` alternate switched on globally, so numbers in tables, KPIs, counts and pagination always align. Hierarchy comes from size and weight steps, not from a second family.

### Hierarchy
- **KPI** (600, 1.75rem / 2.125rem, tight tracking): the two figures in the KPI strip only, preceded by a small subtle `PKR` mark in 13px medium.
- **Headline** (600, 1.25rem / 1.75rem, tight tracking): page titles ("Overview", "Users", "Sign in to The Collector").
- **Title** (500, 1rem / 1.5rem, tight tracking): dialog titles; also the touch-size input text on phones.
- **Body** (400, 0.875rem / 1.375rem): the base size set on `body`; dialog body.
- **Body Dense** (400-500, 0.8125rem / 1.25rem): table cells, panel titles (500), buttons (500), descriptions, inputs, tabs.
- **Label** (500, 0.75rem / 1rem): table headers, field labels, pills, small buttons, bottom-nav labels, hints, pagination ranges. Sentence case, never uppercase-tracked.

### Named Rules
**The Tabular Ledger Rule.** Figures are tabular everywhere; numeric columns, counts and KPIs also carry `tabular-nums` explicitly so the alignment survives any override.

**The Fixed Formats Rule.** Houses are rendered `S-<n>` and amounts `PKR 5,000` through the shared formatters; never inline either format.

## Layout

A shell plus a single content column. On desktop (768px and up) a sticky sidebar sits on the left: a 64px icon rail by default that expands to 232px over the content on hover intent (120ms open delay, 220ms close delay) or keyboard focus, and pushes the content aside when pinned (pin state persists in a cookie). Every rail icon sits on the rail's 32px centre line so nothing moves as it opens. Below 768px the sidebar is replaced by a 56px sticky top bar (logo, theme, logout) and, when there is more than one destination, a 56px bottom tab bar.

Content is capped at 1152px (`max-w-6xl`) and centred, with 16 / 24 / 32px side padding at phone / 640px / 768px, 20px top padding on phones and 32px from 768px, and extra bottom padding on phones to clear the tab bar.

Rhythm: page header to first panel 24px; panel to panel 16px; panel header 12px x 16px; KPI cells 16px x 20px; table cells 16px horizontal; toolbar gaps 8px; form gaps 12-16px. The page header puts title and description left and its toolbar (month stepper, `S-` filter, or the page's primary action) right from 1024px; below that the toolbar wraps under the title.

Breakpoints that change behaviour: 640px (tables switch between columns and stacked rows; dialogs become bottom sheets below it), 768px (sidebar vs top bar and bottom nav), 1024px (page header goes to one row; row-level button labels appear).

### Named Rules
**The Ledger Alignment Rule.** Identifiers and names read left; short fixed-width tokens (relative time, status and role pills) sit centred; amounts and row actions sit right. Tables never centre text columns.

**The No Sideways Scroll Rule.** On phones a table row becomes a stacked mini-row (identifier and status top-left, amount top-right, secondary detail and actions below), never a horizontally scrolling table.

## Elevation & Depth

Flat at rest. Depth is tonal: ground, then surface, then raised surface, separated by hairlines. Shadows appear only on layers that float above the page because of a state change, and they are soft and diffuse, never hard or offset.

### Shadow Vocabulary
- **Sidebar overlay** (`box-shadow: 8px 0 32px rgb(0 0 0 / 0.18)`): only while the sidebar is hover-expanded over content, not when pinned.
- **Toast** (`box-shadow: 0 8px 24px rgb(0 0 0 / 0.18)`): notifications.
- **Dialog** (`box-shadow: 0 16px 48px rgb(0 0 0 / 0.28)`): modals and phone sheets, over a 50% (dark: 70%) black scrim.
- **Segmented thumb edge** (`box-shadow: inset 0 0 0 1px rgb(var(--border-strong))`): an inset hairline, not elevation.

### Named Rules
**The Flat-By-Default Rule.** Panels, cards, buttons and inputs carry no shadow. A shadow means "this layer is temporarily above the page".

## Shapes

Three radii, nested by size: controls (inputs, buttons, nav items, skeletons, segmented well) 6px; panels, toasts and empty-state icon tiles 8px; dialogs 12px (phone sheets round only their top corners). Pills, avatars, count chips and scrollbar thumbs are fully round. Inner elements inside a padded control step down (the segmented thumb is 5px inside a 6px well). Borders are 1px hairlines throughout. The logo mark is an outlined rounded square with two ruled lines.

## Components

### Buttons
Calm, compact and filled only when it matters.
- **Shape:** gently rounded (6px); 36px tall at `md`, 28px at `sm`; square 36px and 28px icon variants.
- **Primary:** ink fill with on-ink text (white in dark, black in light), 500 weight. One per view.
- **Secondary (default):** surface fill, strong-hairline border, ink text; hover to raised surface.
- **Ghost:** no fill, muted ink; hover adds raised surface and full ink. Used for icon actions, steppers, close buttons.
- **Danger:** red fill; only as the confirm button inside a destructive dialog. Row-level Reject and Remove are ghost icon buttons that turn danger-tinted on hover and always confirm in a dialog.
- **States:** 150ms colour transitions, a 0.98 press scale, 50% opacity when disabled. Loading swaps the label for a spinner while keeping the button's width.
- **Touch:** form submit buttons grow to 44px on phones.

### Pills
- **Style:** 22px tall, fully round, 12px medium label, a 6px dot in the same hue, same-hue text on a tinted background.
- **Status:** Approved (green) and Pending approval (grey) via the shared status pill.
- **Role:** Admin (violet), Collector (sky), User (amber) via the shared role pill.
- **Count chip:** a neutral round chip (raised surface, muted ink, tabular) next to panel titles; not a status.

### Panels
- **Corner Style:** 8px.
- **Background:** surface, 1px hairline border, clipped overflow.
- **Shadow Strategy:** none (see Elevation).
- **Header:** a hairline-ruled row, 12px x 16px, 13px medium title with optional count chip on the left and controls on the right; stacks on phones.
- **KPI strip:** one panel split into two cells by a hairline (side by side from 640px, stacked below). Each cell: muted label, `PKR` mark plus KPI figure, and a 12px muted line underneath (the neutral delta or a plain-language status). The Awaiting approval cell is a full-cell button that jumps to the Pending tab.

### Inputs / Fields
- **Style:** surface fill, strong-hairline border, 6px radius, 36px (44px `touch` on phones with 16px text). Fixed prefixes such as `S-` and `PKR` sit inside the field in subtle medium text. Number spinners are hidden.
- **Focus:** border shifts to ink at 40% with a 2px ink ring at 10%; global keyboard focus is a 2px ink outline at 55% with 2px offset.
- **Error / Disabled:** danger border at 60% and a danger ring; the error message sits under the field in 12px danger text, announced as an alert. Disabled is 50% opacity.
- **Field:** 12px medium muted label above, 6px gaps.

### Segmented Tabs
- A 32px ground-coloured well with a hairline border and 2px padding. The selected tab gets a raised-surface thumb with an inset strong hairline that slides between tabs on the shared spring. Counts sit beside labels in subtle tabular text and tick when they change. Arrow keys, Home and End move between tabs.

### Data Table
- **Desktop:** 36px header row on a 50% raised-surface band with 12px subtle labels; 40px rows ruled by hairlines, hover to 40% raised surface. Alignment follows the Ledger Alignment Rule.
- **Phone:** stacked rows with 12px x 16px padding.
- **Motion:** a new result set settles from 50% opacity with rows staggering in (25ms); a removed row slides 24px right and fades while the others glide up; a background refetch dims the old rows to 60%; when the last row leaves, the table waits for the exit to finish before handing over to the empty state.
- **Empty state:** centred 8px-radius hairline tile with a 16px icon, a medium title and one muted line saying what will appear here and what to do.
- **Loading:** skeleton bars shaped like the cells, aligned like the columns. Never spinners.

### Dialog
- Native `<dialog>` with a fading scrim. Desktop: centred, 448px max, 12px radius, 24px padding, scales up from 0.97 over 240ms, ghost close button top-right. Phones: bottom sheet with a grab handle and drag-to-dismiss, 90dvh max, top corners rounded. Footer actions sit right-aligned on desktop and full-width (primary on top) on phones. Closing is blocked while a request is in flight.

### Navigation
- **Sidebar:** surface panel with a hairline right edge. Items are 32px, 13px medium; inactive items are muted with a 60% raised-surface hover; the active item gets a raised-surface pill that slides between items on the spring. Labels fade in after the panel has room and fade out before it narrows. The account block at the foot keeps the avatar on the rail and reveals name, role pill, theme toggle and logout with the panel.
- **Bottom nav (phones):** 56px items, 20px icon over a 12px label; inactive subtle, active ink with a 2px ink bar along the top edge that slides between tabs.
- **Month stepper:** a 36px bordered control with ghost chevrons either side of the month label; the label slides in the direction of travel, and tapping it opens the native month picker. Future months are disabled.

### Approval Hand-off (signature)
Approve is optimistic: the row leaves the Pending table immediately, the Pending tab count and Awaiting approval figure tick down, and the Approved count and month total tick up over 500ms with exponential ease-out. Numbers never count up on first load; they only animate when a value changes.

## Do's and Don'ts

### Do:
- **Do** use only the token colours (`bg`, `surface`, `fg`, `border`, `success`, `pending`, `danger`, `role-*`) and define every new token for both `:root` and `.dark` as RGB triplets.
- **Do** keep green for Approved and grey for Pending; write trends and deltas in neutral ink with an arrow and a sign.
- **Do** use violet for admin, sky for collector and amber for user, and only inside the role pill.
- **Do** spend one ink-filled primary button per view; everything else is secondary or ghost.
- **Do** put content in panels (8px radius, hairline border, surface fill) and keep panels one level deep.
- **Do** align identifiers and names left, relative times and pills centre, amounts and row actions right.
- **Do** use the shared motion presets: exponential ease-out `cubic-bezier(0.16, 1, 0.3, 1)`, the 500/40 spring for layout moves, exits faster than entrances, and reduced motion honoured.
- **Do** show loading with skeletons shaped like the content, and write empty states that say what will appear and what to do.
- **Do** keep collector inputs and submit buttons at 44px on phones.

### Don't:
- **Don't** introduce a brand accent or use raw Tailwind palettes (zinc, blue, etc.).
- **Don't** use green, grey-pill styling or role colours for anything other than status and role.
- **Don't** use danger red outside destructive actions and invalid input.
- **Don't** use `chart-1` until the charts ship.
- **Don't** nest panels or build floating KPI cards; the KPI strip is one panel split by a hairline.
- **Don't** centre text columns in tables or let tables scroll sideways on phones.
- **Don't** animate for decoration: no count-up on page load, no ambient loops, no entrance flourishes beyond the route settle.
- **Don't** add shadows to resting surfaces.
- **Don't** convey status or role by colour alone.
