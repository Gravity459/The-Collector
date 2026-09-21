"use client";

import { useState } from "react";

import { useCollections } from "@/lib/queries";

import { CollectionForm } from "./CollectionForm";
import { CollectionsTable } from "./CollectionsTable";
import { HouseFilter } from "./HouseFilter";
import { Pagination } from "./Pagination";

export function UserView() {
  const [page, setPage] = useState(1);
  const [houseNumber, setHouseNumber] = useState<number | null>(null);

  const { data, isLoading } = useCollections({
    page,
    size: 10,
    house_number: houseNumber,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
          Overview
        </h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Submit a collection and track this month&apos;s payments.
        </p>
      </div>

      <CollectionForm />

      <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
            This month&apos;s payments
          </h2>
          <HouseFilter
            value={houseNumber}
            onChange={(v) => {
              setHouseNumber(v);
              setPage(1);
            }}
          />
        </div>
        <CollectionsTable
          items={data?.items ?? []}
          isLoading={isLoading}
          mode="status"
        />
        <Pagination
          page={data?.page ?? page}
          totalPages={data?.total_pages ?? 0}
          onChange={setPage}
        />
      </div>
    </div>
  );
}
