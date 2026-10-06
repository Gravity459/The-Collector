"use client";

import { ArrowDownRight, ArrowUpRight, CircleCheck, Inbox } from "lucide-react";
import * as m from "motion/react-m";
import { useState } from "react";

import { cn } from "@/lib/cn";
import {
  CURRENCY,
  currentMonth,
  formatMonthName,
  formatNumber,
  shiftMonth,
} from "@/lib/format";
import { ease, fadeIn } from "@/lib/motion";
import { useCollectionTotal, useCollections } from "@/lib/queries";

import { CollectionsTable } from "./CollectionsTable";
import { HouseFilter } from "./HouseFilter";
import { MonthFilter } from "./MonthFilter";
import { PageHeader } from "./PageHeader";
import { Pagination } from "./Pagination";
import { AnimatedNumber } from "./ui/AnimatedNumber";
import { Panel } from "./ui/Panel";
import { SegmentedTabs } from "./ui/SegmentedTabs";
import { Skeleton } from "./ui/Skeleton";

type Tab = "pending" | "approved";

/** One cell of the KPI strip. `onActivate` makes the whole cell a button. */
function Kpi({
  label,
  value,
  loading,
  stale,
  onActivate,
  activateHint,
  children,
}: {
  label: string;
  value: number | undefined;
  loading: boolean;
  /** Previous filter's value still shown while the new one loads: dim it. */
  stale?: boolean;
  onActivate?: () => void;
  /** Screen-reader hint appended after the visible content. */
  activateHint?: string;
  children?: React.ReactNode;
}) {
  const body = (
    <>
      <span className="block text-sm text-fg-muted">{label}</span>
      <span
        className={cn(
          "mt-1.5 flex items-baseline gap-2 transition-opacity duration-200",
          stale && "opacity-60",
        )}
      >
        <span className="text-sm font-medium text-fg-subtle">{CURRENCY}</span>
        {loading || value === undefined ? (
          <Skeleton className="h-8 w-32" />
        ) : (
          <m.span variants={fadeIn} initial="initial" animate="animate">
            <AnimatedNumber
              value={value}
              format={(n) => formatNumber(Math.round(n))}
              className="text-kpi font-semibold tabular-nums tracking-tight text-fg"
            />
          </m.span>
        )}
      </span>
      <span className="mt-1 block min-h-5 text-xs text-fg-muted">
        {children != null && children !== false && (
          <m.span className="block" variants={fadeIn} initial="initial" animate="animate">
            {children}
          </m.span>
        )}
      </span>
    </>
  );

  if (onActivate) {
    return (
      <button
        type="button"
        onClick={onActivate}
        // inset ring: the panel clips anything drawn outside the cell
        className="block w-full px-5 py-4 text-left transition-colors duration-150 hover:bg-surface-2/40 focus-visible:outline-offset-[-2px]"
      >
        {body}
        {activateHint && <span className="sr-only">{activateHint}</span>}
      </button>
    );
  }
  return <div className="px-5 py-4">{body}</div>;
}

/**
 * Change vs the previous month. Neutral ink: green/grey are reserved for
 * status, so direction is carried by the arrow and sign. For the month in
 * progress it says so, since a partial month is compared with a full one.
 */
function Delta({
  current,
  previous,
  month,
}: {
  current?: number;
  previous?: number;
  month: string;
}) {
  if (current === undefined || previous === undefined) return null;
  const prevName = formatMonthName(shiftMonth(month, -1));
  const partial = month === currentMonth();
  if (previous === 0) {
    return (
      <span>
        {current === 0 ? "Nothing approved yet" : `Nothing approved in ${prevName}`}
      </span>
    );
  }
  const pct = Math.round(((current - previous) / previous) * 100);
  const up = pct >= 0;
  const Icon = up ? ArrowUpRight : ArrowDownRight;
  return (
    <span className="inline-flex flex-wrap items-center gap-1">
      {partial && <span>So far,</span>}
      <span className="inline-flex items-center font-medium text-fg">
        <Icon className="h-3.5 w-3.5" aria-hidden />
        {up ? "+" : "−"}
        {Math.abs(pct)}%
      </span>
      <span>vs {partial ? `all of ${prevName}` : prevName}</span>
    </span>
  );
}

export function AdminView() {
  const [tab, setTab] = useState<Tab>("pending");
  // the panel only slides once the user has switched tabs, not on first load
  const [switched, setSwitched] = useState(false);
  const [houseNumber, setHouseNumber] = useState<number | null>(null);
  const [pendingPage, setPendingPage] = useState(1);
  const [approvedPage, setApprovedPage] = useState(1);
  const [month, setMonth] = useState(currentMonth);

  const pending = useCollections({
    page: pendingPage,
    size: 10,
    house_number: houseNumber,
    approved: false,
  });
  const approved = useCollections({
    page: approvedPage,
    size: 10,
    house_number: houseNumber,
    approved: true,
    month,
  });
  const total = useCollectionTotal({ approved: true, month });
  const previousTotal = useCollectionTotal({
    approved: true,
    month: shiftMonth(month, -1),
  });
  const pendingTotal = useCollectionTotal({ approved: false });

  const active = tab === "pending" ? pending : approved;
  // tabs slide in the direction of travel: Pending (left) <-> Approved (right)
  const dir = tab === "approved" ? 1 : -1;
  const pendingCount = pending.data?.total;
  const totalsSettled = !total.isPlaceholderData && !previousTotal.isPlaceholderData;

  function selectTab(t: Tab) {
    setSwitched(true);
    setTab(t);
  }

  return (
    <div>
      <PageHeader
        title="Overview"
        description="Approve what collectors submitted and track the month's total."
      >
        <MonthFilter
          value={month}
          onChange={(v) => {
            setMonth(v);
            setApprovedPage(1);
          }}
        />
        <HouseFilter
          value={houseNumber}
          onChange={(v) => {
            setHouseNumber(v);
            setPendingPage(1);
            setApprovedPage(1);
          }}
        />
      </PageHeader>

      {/* One bordered strip split by a hairline, not two floating cards. */}
      <Panel className="mb-4 grid divide-y divide-border sm:grid-cols-2 sm:divide-x sm:divide-y-0">
        <Kpi
          label={`Approved in ${formatMonthName(month)}`}
          value={total.data?.total}
          loading={total.isLoading}
          stale={total.isPlaceholderData}
        >
          {totalsSettled && (
            <Delta
              current={total.data?.total}
              previous={previousTotal.data?.total}
              month={month}
            />
          )}
        </Kpi>
        <Kpi
          label="Awaiting approval"
          value={pendingTotal.data?.total}
          loading={pendingTotal.isLoading}
          onActivate={() => selectTab("pending")}
          activateHint="Show pending collections"
        >
          {pendingCount !== undefined &&
            (pendingCount === 0
              ? "All caught up"
              : `${pendingCount} ${pendingCount === 1 ? "collection" : "collections"} to review`)}
        </Kpi>
      </Panel>

      <Panel>
        <div className="flex flex-col gap-3 border-b border-border px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <SegmentedTabs<Tab>
            label="Collections"
            idBase="collections"
            value={tab}
            onChange={selectTab}
            items={[
              { value: "pending", label: "Pending", count: pending.data?.total },
              { value: "approved", label: "Approved", count: approved.data?.total },
            ]}
          />
          <p className="text-xs text-fg-subtle">
            {tab === "pending"
              ? "Across all months"
              : `Approved in ${formatMonthName(month)}`}
          </p>
        </div>

        {/* Keyed, not AnimatePresence: the new view slides in at once instead
            of waiting for the old one (and its rows) to animate out. */}
        <m.div
          key={tab}
          initial={switched ? { opacity: 0, x: dir * 12 } : false}
          animate={{ opacity: 1, x: 0, transition: { duration: 0.22, ease } }}
          role="tabpanel"
          id={`collections-panel-${tab}`}
          aria-labelledby={`collections-tab-${tab}`}
        >
          {tab === "pending" ? (
            <CollectionsTable
              items={pending.data?.items ?? []}
              isLoading={pending.isLoading}
              isFetching={pending.isPlaceholderData}
              pageKey={`pending-${pendingPage}-${houseNumber}`}
              mode="approve"
              caption="Collections awaiting approval"
              empty={{
                icon: CircleCheck,
                title: houseNumber
                  ? "Nothing pending for this house"
                  : "Nothing waiting for approval",
                description: "New submissions from collectors appear here.",
              }}
            />
          ) : (
            <CollectionsTable
              items={approved.data?.items ?? []}
              isLoading={approved.isLoading}
              isFetching={approved.isPlaceholderData}
              pageKey={`approved-${approvedPage}-${houseNumber}-${month}`}
              mode="status"
              withRemove
              caption={`Approved payments in ${formatMonthName(month)}`}
              empty={{
                icon: Inbox,
                title: `No approved payments in ${formatMonthName(month)}`,
                description: "Approve pending collections and they'll be counted here.",
              }}
            />
          )}
          <Pagination
            page={active.data?.page ?? 1}
            totalPages={active.data?.total_pages ?? 0}
            total={active.data?.total ?? 0}
            onChange={tab === "pending" ? setPendingPage : setApprovedPage}
          />
        </m.div>
      </Panel>
    </div>
  );
}
