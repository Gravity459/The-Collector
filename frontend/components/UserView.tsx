"use client";

import { Inbox, ReceiptText } from "lucide-react";
import { useState } from "react";

import { currentMonth, formatMonth, formatMonthName } from "@/lib/format";
import { useCollections } from "@/lib/queries";
import type { Role } from "@/lib/types";

import { CollectionForm } from "./CollectionForm";
import { CollectionsTable } from "./CollectionsTable";
import { HouseFilter } from "./HouseFilter";
import { MonthFilter } from "./MonthFilter";
import { PageHeader } from "./PageHeader";
import { Pagination } from "./Pagination";
import { Panel, PanelHeader } from "./ui/Panel";

/**
 * Non-admin Overview. Collectors submit and see this month's rows;
 * users only browse approved payments (the backend enforces both).
 */
export function UserView({ role }: { role: Role }) {
  const isCollector = role === "collector";
  const [page, setPage] = useState(1);
  const [houseNumber, setHouseNumber] = useState<number | null>(null);
  const [month, setMonth] = useState(currentMonth);

  const { data, isLoading, isPlaceholderData } = useCollections({
    page,
    size: 10,
    house_number: houseNumber,
    month: isCollector ? null : month,
  });

  return (
    <div>
      <PageHeader
        title="Overview"
        description={
          isCollector
            ? `Log each payment as you collect it. Showing ${formatMonth(currentMonth())}.`
            : "Check which payments have been approved, by month and house."
        }
      />

      <div className="space-y-4">
        {isCollector && <CollectionForm />}

        <Panel>
          <PanelHeader
            title={isCollector ? "This month" : "Approved payments"}
            count={data?.total}
          >
            <div className="flex flex-wrap items-center gap-2">
              {!isCollector && (
                <MonthFilter
                  value={month}
                  onChange={(v) => {
                    setMonth(v);
                    setPage(1);
                  }}
                />
              )}
              <div className="flex-1 sm:flex-none">
                <HouseFilter
                  value={houseNumber}
                  onChange={(v) => {
                    setHouseNumber(v);
                    setPage(1);
                  }}
                />
              </div>
            </div>
          </PanelHeader>
          <CollectionsTable
            items={data?.items ?? []}
            isLoading={isLoading}
            isFetching={isPlaceholderData}
            pageKey={`${page}-${houseNumber}-${month}`}
            mode="status"
            caption={isCollector ? "Your collections this month" : "Approved payments"}
            empty={
              isCollector
                ? {
                    icon: ReceiptText,
                    title: houseNumber ? "No collections for this house yet" : "No collections this month yet",
                    description: "Use the form above to log a payment; it shows here as pending until an admin approves it.",
                  }
                : {
                    icon: Inbox,
                    title: `No approved payments in ${formatMonthName(month)}`,
                    description: "Try another month or clear the house filter.",
                  }
            }
          />
          <Pagination
            page={data?.page ?? page}
            totalPages={data?.total_pages ?? 0}
            total={data?.total ?? 0}
            onChange={setPage}
          />
        </Panel>
      </div>
    </div>
  );
}
