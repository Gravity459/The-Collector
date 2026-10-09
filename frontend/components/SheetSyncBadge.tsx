import { CircleAlert, Clock, FileSpreadsheet } from "lucide-react";

import { cn } from "@/lib/cn";
import type { SheetSyncSummary } from "@/lib/types";

/**
 * Where an approved payment stands in the Google Sheet. Icon + words in plain
 * ink, never a pill: pills (and green/grey) belong to payment status.
 */
export function SheetSyncBadge({ sync }: { sync: SheetSyncSummary | null }) {
  if (!sync) {
    return <span className="text-fg-subtle">—</span>;
  }

  const { Icon, label, title, tone } = (() => {
    switch (sync.status) {
      case "done":
        return {
          Icon: FileSpreadsheet,
          label: sync.target_cell ? `Cell ${sync.target_cell}` : "In sheet",
          title: "Written to the Google Sheet",
          tone: "text-fg-muted",
        };
      case "pending":
        return {
          Icon: Clock,
          label: "Syncing",
          title: "Being written to the Google Sheet",
          tone: "text-fg-subtle",
        };
      case "needs_review":
        return {
          Icon: CircleAlert,
          label: "Needs review",
          title: "Not written yet. See “Sheet needs attention” above.",
          tone: "text-danger",
        };
      default:
        return {
          Icon: CircleAlert,
          label: "Sync failed",
          title: "Not written yet. It retries daily, or retry it above.",
          tone: "text-danger",
        };
    }
  })();

  return (
    <span
      title={title}
      className={cn("inline-flex items-center gap-1.5 whitespace-nowrap text-xs", tone)}
    >
      <Icon aria-hidden className="h-3.5 w-3.5 shrink-0" />
      {label}
    </span>
  );
}
