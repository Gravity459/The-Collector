"use client";

import type { LucideIcon } from "lucide-react";

import { formatAmount, formatDate, houseLabel, relativeTime } from "@/lib/format";
import type { Collection } from "@/lib/types";

import { ApproveButton } from "./ApproveButton";
import { RejectButton } from "./RejectButton";
import { RemoveButton } from "./RemoveButton";
import { StatusPill } from "./StatusPill";
import { type Column, DataTable } from "./ui/DataTable";
import { EmptyState } from "./ui/EmptyState";

interface Props {
  items: Collection[];
  isLoading?: boolean;
  /** "status" shows a StatusPill; "approve" shows Approve / Reject actions. */
  mode: "status" | "approve";
  /** Append a Remove action (used for approved payments). */
  withRemove?: boolean;
  caption: string;
  empty: { icon: LucideIcon; title: string; description?: string };
  /** See DataTable: identity of the result set, and background refetch. */
  pageKey?: string;
  isFetching?: boolean;
}

export function CollectionsTable({
  items,
  isLoading,
  mode,
  withRemove,
  caption,
  empty,
  pageKey,
  isFetching,
}: Props) {
  const columns: Column<Collection>[] = [
    {
      key: "house",
      header: "House",
      mobile: "primary",
      cell: (c) => (
        <span className="font-medium text-fg">{houseLabel(c.house_number)}</span>
      ),
    },
    {
      key: "collector",
      header: "Collector",
      cell: (c) => (
        <span className="text-fg-muted">{c.collector_name ?? "Former collector"}</span>
      ),
    },
    {
      key: "submitted",
      header: "Submitted",
      align: "center",
      cell: (c) => (
        <time dateTime={c.created_at} title={formatDate(c.created_at)} className="whitespace-nowrap text-fg-muted">
          {relativeTime(c.created_at)}
        </time>
      ),
    },
    ...(mode === "status"
      ? [
          {
            key: "status",
            header: "Status",
            align: "center",
            mobile: "primary",
            cell: (c) => <StatusPill approved={c.approved} />,
          } satisfies Column<Collection>,
        ]
      : []),
    {
      key: "amount",
      header: "Amount",
      align: "center",
      numeric: true,
      mobile: "end",
      cell: (c) => <span className="font-medium text-fg">{formatAmount(c.amount)}</span>,
    },
  ];

  if (mode === "approve") {
    columns.push({
      key: "actions",
      header: "Actions",
      align: "center",
      mobile: "actions",
      className: "whitespace-nowrap",
      cell: (c) => (
        <span className="inline-flex items-center justify-center gap-1">
          <RejectButton collection={c} />
          <ApproveButton collection={c} />
        </span>
      ),
    });
  } else if (withRemove) {
    columns.push({
      key: "remove",
      header: "Remove",
      align: "center",
      mobile: "actions",
      className: "whitespace-nowrap",
      cell: (c) => <RemoveButton collection={c} />,
    });
  }

  return (
    <DataTable
      columns={columns}
      rows={items}
      getRowId={(c) => c.id}
      isLoading={isLoading}
      isFetching={isFetching}
      pageKey={pageKey}
      layout="fixed"
      caption={caption}
      empty={<EmptyState {...empty} />}
    />
  );
}
