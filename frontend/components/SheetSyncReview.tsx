"use client";

import { useState } from "react";

import { formatAmount, formatMonth, houseLabel } from "@/lib/format";
import { useOverwriteSheetJob, useRetrySheetJob, useSheetSyncJobs } from "@/lib/queries";
import type { SheetSyncJob } from "@/lib/types";

import { ConfirmModal } from "./ConfirmModal";
import { Pagination } from "./Pagination";
import { Button } from "./ui/Button";
import { Panel } from "./ui/Panel";

/** What happened and what to do about it, in the admin's terms. */
function explain(job: SheetSyncJob): { what: string; fix?: string } {
  const house = houseLabel(job.house_number);
  const month = formatMonth(job.period_month);
  switch (job.reason) {
    case "conflict":
      return {
        what: `Cell ${job.target_cell} already holds “${job.existing_value}”.`,
        fix: `Overwrite it with ${formatAmount(job.amount)} if this payment is the right one.`,
      };
    case "house_not_in_sheet":
      return {
        what: `${house} isn't in the sheet's house column.`,
        fix: "Add a row for it in the sheet, then retry.",
      };
    case "month_column_missing":
      return {
        what: `The sheet has no ${month} column.`,
        fix: "New columns are only added after the newest month. Add this one by hand, then retry.",
      };
    case "layout_unreadable":
      return {
        what: "The sheet's layout couldn't be read reliably.",
        fix: "Check the header row and house column look normal, then retry.",
      };
    default:
      return {
        what: "Google Sheets or the AI couldn't be reached.",
        fix: "It retries every day. Retry now if the problem is fixed.",
      };
  }
}

function JobRow({ job }: { job: SheetSyncJob }) {
  const [confirming, setConfirming] = useState(false);
  const overwrite = useOverwriteSheetJob();
  const retry = useRetrySheetJob();
  const { what, fix } = explain(job);
  const house = houseLabel(job.house_number);
  const isConflict = job.reason === "conflict";
  const busy = overwrite.isPending || retry.isPending;

  return (
    <li className="flex flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:gap-6">
      <div className="min-w-0 flex-1">
        <p className="text-sm text-fg">
          <span className="font-medium">{house}</span>
          <span className="text-fg-muted">
            {" "}
            for {formatMonth(job.period_month)}, {formatAmount(job.amount)}
          </span>
        </p>
        <p className="mt-0.5 text-sm text-fg-muted">
          {what} {fix}
        </p>
        {/* technical detail only where it adds to the sentence above */}
        {job.error && (job.status === "failed" || job.reason === "layout_unreadable") && (
          <details className="mt-1 text-xs text-fg-subtle">
            <summary className="cursor-pointer select-none">Details</summary>
            <p className="mt-1 break-words">{job.error}</p>
          </details>
        )}
      </div>
      {isConflict ? (
        <Button
          variant="secondary"
          size="sm"
          className="self-start sm:self-center"
          loading={overwrite.isPending}
          disabled={busy}
          onClick={() => setConfirming(true)}
        >
          Overwrite cell
        </Button>
      ) : (
        <Button
          variant="secondary"
          size="sm"
          className="self-start sm:self-center"
          loading={retry.isPending}
          disabled={busy}
          onClick={() => retry.mutate(job)}
        >
          Retry
        </Button>
      )}

      {isConflict && (
        <ConfirmModal
          open={confirming}
          title={`Overwrite cell ${job.target_cell}?`}
          message={`${house}'s ${formatMonth(job.period_month)} cell holds “${job.existing_value}”. It will be replaced with ${formatAmount(job.amount)}.`}
          confirmLabel="Overwrite cell"
          loading={overwrite.isPending}
          onConfirm={() =>
            overwrite.mutate(job, { onSettled: () => setConfirming(false) })
          }
          onCancel={() => setConfirming(false)}
        />
      )}
    </li>
  );
}

/**
 * Approved payments that didn't make it into the Google Sheet. Renders
 * nothing while every write has gone through.
 */
export function SheetSyncReview() {
  const [page, setPage] = useState(1);
  const jobs = useSheetSyncJobs(page);
  const data = jobs.data;
  if (!data || data.total === 0) return null;

  return (
    <Panel aria-labelledby="sheet-review-title" className="mb-4">
      <div className="border-b border-border px-4 py-3">
        <h2 id="sheet-review-title" className="text-sm font-medium text-fg">
          Sheet needs attention
          <span className="ml-2 font-normal text-fg-muted">{data.total}</span>
        </h2>
        <p className="mt-0.5 text-xs text-fg-subtle">
          These approved payments aren&rsquo;t in the Google Sheet yet.
        </p>
      </div>
      <ul className="divide-y divide-border">
        {data.items.map((job) => (
          <JobRow key={job.id} job={job} />
        ))}
      </ul>
      {data.total_pages > 1 && (
        <Pagination
          page={data.page}
          totalPages={data.total_pages}
          total={data.total}
          onChange={setPage}
        />
      )}
    </Panel>
  );
}
