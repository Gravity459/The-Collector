import type { Collection } from "@/lib/types";

import { ApproveButton } from "./ApproveButton";
import { RemoveButton } from "./RemoveButton";
import { StatusPill } from "./StatusPill";

interface Props {
  items: Collection[];
  isLoading?: boolean;
  /** "status" shows a StatusPill; "approve" shows an Approve action. */
  mode: "status" | "approve";
  /** Append a Remove action column (used for approved payments). */
  withRemove?: boolean;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function CollectionsTable({ items, isLoading, mode, withRemove }: Props) {
  const colCount = 4 + (withRemove ? 1 : 0);
  const th =
    "px-4 py-3 text-center text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400";
  const td = "px-4 py-3 text-center align-middle text-sm";

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] border-collapse">
        <thead className="border-b border-zinc-200 dark:border-zinc-800">
          <tr>
            <th className={th}>House</th>
            <th className={th}>Amount</th>
            <th className={th}>Submitted</th>
            <th className={th}>{mode === "approve" ? "Action" : "Status"}</th>
            {withRemove && <th className={th}>Remove</th>}
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/70">
          {isLoading && (
            <tr>
              <td
                colSpan={colCount}
                className="px-4 py-10 text-center text-sm text-zinc-400"
              >
                Loading…
              </td>
            </tr>
          )}
          {!isLoading && items.length === 0 && (
            <tr>
              <td
                colSpan={colCount}
                className="px-4 py-10 text-center text-sm text-zinc-400"
              >
                No records.
              </td>
            </tr>
          )}
          {items.map((c) => (
            <tr
              key={c.id}
              className="transition-colors hover:bg-zinc-50 dark:hover:bg-zinc-800/40"
            >
              <td className={`${td} font-medium text-zinc-900 dark:text-zinc-100`}>
                S-{c.house_number}
              </td>
              <td className={`${td} tabular-nums text-zinc-700 dark:text-zinc-300`}>
                {c.amount}
              </td>
              <td className={`${td} text-zinc-500 dark:text-zinc-400`}>
                {formatDate(c.created_at)}
              </td>
              <td className={td}>
                <div className="flex justify-center">
                  {mode === "approve" ? (
                    <ApproveButton id={c.id} />
                  ) : (
                    <StatusPill approved={c.approved} />
                  )}
                </div>
              </td>
              {withRemove && (
                <td className={td}>
                  <div className="flex justify-center">
                    <RemoveButton id={c.id} houseNumber={c.house_number} />
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
