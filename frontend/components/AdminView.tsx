"use client";

import { useState } from "react";

import { useCollections, useCurrentMonthTotal } from "@/lib/queries";

import { CollectionsTable } from "./CollectionsTable";
import { HouseFilter } from "./HouseFilter";
import { Pagination } from "./Pagination";

export function AdminView() {
  const [houseNumber, setHouseNumber] = useState<number | null>(null);
  const [pendingPage, setPendingPage] = useState(1);
  const [approvedPage, setApprovedPage] = useState(1);

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
  });
  const total = useCurrentMonthTotal();

  const monthLabel = new Date().toLocaleString(undefined, {
    month: "long",
    year: "numeric",
  });

  const card =
    "overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
            Overview
          </h1>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Review pending collections and manage approved payments.
          </p>
        </div>
        <HouseFilter
          value={houseNumber}
          onChange={(v) => {
            setHouseNumber(v);
            setPendingPage(1);
            setApprovedPage(1);
          }}
        />
      </div>

      <section className={`${card} p-5`}>
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
          Total approved collection · {monthLabel}
        </p>
        <p className="mt-1 text-3xl font-semibold tabular-nums tracking-tight text-zinc-900 dark:text-zinc-100">
          {total.isLoading ? "…" : (total.data?.total ?? 0).toLocaleString()}
        </p>
      </section>

      <section className={card}>
        <div className="flex items-center gap-2 p-4">
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
            For approval
          </h2>
          <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
            {pending.data?.total ?? 0}
          </span>
        </div>
        <CollectionsTable
          items={pending.data?.items ?? []}
          isLoading={pending.isLoading}
          mode="approve"
        />
        <Pagination
          page={pending.data?.page ?? pendingPage}
          totalPages={pending.data?.total_pages ?? 0}
          onChange={setPendingPage}
        />
      </section>

      <section className={card}>
        <div className="flex items-center gap-2 p-4">
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
            Approved payments
          </h2>
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-500/15 dark:text-green-400">
            {approved.data?.total ?? 0}
          </span>
        </div>
        <CollectionsTable
          items={approved.data?.items ?? []}
          isLoading={approved.isLoading}
          mode="status"
          withRemove
        />
        <Pagination
          page={approved.data?.page ?? approvedPage}
          totalPages={approved.data?.total_pages ?? 0}
          onChange={setApprovedPage}
        />
      </section>
    </div>
  );
}
