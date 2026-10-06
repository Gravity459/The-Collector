import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "./ui/Button";

interface Props {
  page: number;
  totalPages: number;
  /** Total number of rows across all pages. */
  total: number;
  size?: number;
  onChange: (page: number) => void;
}

/** Panel footer: "11–20 of 47" + prev/next. Hidden when everything fits on one page. */
export function Pagination({ page, totalPages, total, size = 10, onChange }: Props) {
  if (totalPages <= 1) return null;
  const from = (page - 1) * size + 1;
  const to = Math.min(page * size, total);

  return (
    <div className="flex items-center justify-between gap-3 border-t border-border px-4 py-2.5">
      <span className="text-xs tabular-nums text-fg-muted">
        {from}–{to} of {total}
      </span>
      <div className="flex gap-1">
        <Button
          variant="secondary"
          size="icon-sm"
          aria-label="Previous page"
          disabled={page <= 1}
          onClick={() => onChange(page - 1)}
        >
          <ChevronLeft className="h-4 w-4" aria-hidden />
        </Button>
        <Button
          variant="secondary"
          size="icon-sm"
          aria-label="Next page"
          disabled={page >= totalPages}
          onClick={() => onChange(page + 1)}
        >
          <ChevronRight className="h-4 w-4" aria-hidden />
        </Button>
      </div>
    </div>
  );
}
