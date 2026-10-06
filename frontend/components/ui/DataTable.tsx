"use client";

import { AnimatePresence } from "motion/react";
import * as m from "motion/react-m";
import { useRef, useState } from "react";

import { cn } from "@/lib/cn";
import { fadeIn, list, row as rowVariants, spring } from "@/lib/motion";

import { Skeleton } from "./Skeleton";

/** Where a column lands in the stacked phone layout. */
type MobileSlot = "primary" | "end" | "secondary" | "actions" | "hide";

type Align = "left" | "center" | "right";

export interface Column<T> {
  key: string;
  header: string;
  cell: (row: T) => React.ReactNode;
  /**
   * Text columns read left (default); short fixed-width tokens such as
   * pills and relative times sit centre; amounts and row actions sit right.
   */
  align?: Align;
  /** Numeric column: tabular figures. */
  numeric?: boolean;
  /** Extra classes for this column's cells (desktop). */
  className?: string;
  mobile?: MobileSlot;
  /** Hide the header text while keeping it for assistive tech. */
  srHeader?: boolean;
}

interface Props<T> {
  columns: Column<T>[];
  rows: T[];
  getRowId: (row: T) => string;
  isLoading?: boolean;
  /** Background refetch with the previous page still shown: rows dim slightly. */
  isFetching?: boolean;
  /**
   * Identity of the current result set (page + filters). When it changes the
   * new rows fade in over the old ones instead of popping.
   */
  pageKey?: string;
  /** Rendered when not loading and there are no rows. */
  empty: React.ReactNode;
  /** Accessible table caption. */
  caption: string;
  skeletonRows?: number;
  /** "fixed": every column gets an equal share of the width (even spacing). */
  layout?: "auto" | "fixed";
}

const ALIGN: Record<Align, string> = {
  left: "text-left",
  center: "text-center",
  right: "text-right",
};

const SKELETON_ALIGN: Record<Align, string> = {
  left: "",
  center: "mx-auto",
  right: "ml-auto",
};

/**
 * Dense data table. Below `sm` each row becomes a stacked mini-card instead
 * of scrolling sideways. Rows stagger in when a result set arrives, slide
 * out when removed (approve / reject / remove), and the remaining rows
 * glide up into place.
 */
export function DataTable<T>({
  columns,
  rows,
  getRowId,
  isLoading,
  isFetching,
  pageKey = "default",
  empty,
  caption,
  skeletonRows = 5,
  layout = "auto",
}: Props<T>) {
  // Only adopt a new result-set key once its data has arrived; while the
  // previous page is shown as a placeholder, keep the old key so the rows
  // don't remount twice.
  const committedKey = useRef(pageKey);
  if (!isFetching) committedKey.current = pageKey;
  const setKey = committedKey.current;

  // When the last row of a result set is removed, keep the table mounted until
  // its exit animation finishes, then hand over to the empty state.
  const lastKeyWithRows = useRef<string | null>(null);
  if (rows.length > 0) lastKeyWithRows.current = setKey;
  const [drained, setDrained] = useState(rows.length === 0);
  if (rows.length > 0 && drained) setDrained(false);
  const draining =
    !isLoading && rows.length === 0 && !drained && lastKeyWithRows.current === setKey;
  const onExitComplete = () => {
    if (rows.length === 0) setDrained(true);
  };

  if (!isLoading && rows.length === 0 && !draining) {
    return (
      <m.div key="empty" variants={fadeIn} initial="initial" animate="animate">
        {empty}
      </m.div>
    );
  }

  const slot = (s: MobileSlot) => columns.filter((c) => (c.mobile ?? "secondary") === s);
  const dim = cn(
    "transition-opacity duration-200",
    isFetching && !isLoading && "opacity-60",
  );

  return (
    <>
      {/* Desktop / tablet */}
      <div className="hidden overflow-x-auto sm:block">
        <table className={cn("w-full border-collapse text-sm", layout === "fixed" && "table-fixed")}>
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr className="border-b border-border bg-surface-2/50">
              {columns.map((c) => (
                <th
                  key={c.key}
                  scope="col"
                  className={cn(
                    "h-9 px-4 text-xs font-medium text-fg-subtle",
                    ALIGN[c.align ?? "left"],
                  )}
                >
                  <span className={cn(c.srHeader && "sr-only")}>{c.header}</span>
                </th>
              ))}
            </tr>
          </thead>
          {isLoading ? (
            <tbody>
              {Array.from({ length: skeletonRows }, (_, i) => (
                <tr key={i} className="border-b border-border last:border-0">
                  {columns.map((c) => (
                    <td key={c.key} className="h-10 px-4">
                      <Skeleton
                        className={cn("h-3.5 w-16", SKELETON_ALIGN[c.align ?? "left"])}
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          ) : (
            <m.tbody
              key={setKey}
              variants={list}
              initial="initial"
              animate="animate"
              className={dim}
            >
              <AnimatePresence onExitComplete={onExitComplete}>
                {rows.map((r) => (
                  <m.tr
                    key={getRowId(r)}
                    layout="position"
                    variants={rowVariants}
                    exit="exit"
                    transition={{ layout: spring }}
                    className="border-b border-border transition-colors duration-150 last:border-0 hover:bg-surface-2/40"
                  >
                    {columns.map((c) => (
                      <td
                        key={c.key}
                        className={cn(
                          "h-10 px-4 align-middle",
                          ALIGN[c.align ?? "left"],
                          c.numeric && "tabular-nums",
                          c.className,
                        )}
                      >
                        {c.cell(r)}
                      </td>
                    ))}
                  </m.tr>
                ))}
              </AnimatePresence>
            </m.tbody>
          )}
        </table>
      </div>

      {/* Phone: stacked rows */}
      {isLoading ? (
        <ul className="divide-y divide-border sm:hidden" aria-label={caption}>
          {Array.from({ length: skeletonRows }, (_, i) => (
            <li key={i} className="space-y-2 px-4 py-3">
              <div className="flex justify-between">
                <Skeleton className="h-4 w-14" />
                <Skeleton className="h-4 w-20" />
              </div>
              <Skeleton className="h-3 w-32" />
            </li>
          ))}
        </ul>
      ) : (
        <m.ul
          key={setKey}
          variants={list}
          initial="initial"
          animate="animate"
          className={cn("divide-y divide-border sm:hidden", dim)}
          aria-label={caption}
        >
          <AnimatePresence onExitComplete={onExitComplete}>
            {rows.map((r) => (
              <m.li
                key={getRowId(r)}
                layout="position"
                variants={rowVariants}
                exit="exit"
                transition={{ layout: spring }}
                className="px-4 py-3"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex min-w-0 items-center gap-2">
                    {slot("primary").map((c) => (
                      <span key={c.key} className="min-w-0">
                        {c.cell(r)}
                      </span>
                    ))}
                  </div>
                  <div className="flex shrink-0 items-center gap-2 tabular-nums">
                    {slot("end").map((c) => (
                      <span key={c.key}>{c.cell(r)}</span>
                    ))}
                  </div>
                </div>
                <div className="mt-1.5 flex items-center justify-between gap-3">
                  <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1 text-xs text-fg-muted">
                    {slot("secondary").map((c) => (
                      <span key={c.key} className="min-w-0">
                        {c.cell(r)}
                      </span>
                    ))}
                  </div>
                  {slot("actions").length > 0 && (
                    <div className="flex shrink-0 items-center gap-1.5">
                      {slot("actions").map((c) => (
                        <span key={c.key} className="flex items-center gap-1.5">
                          {c.cell(r)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </m.li>
            ))}
          </AnimatePresence>
        </m.ul>
      )}
    </>
  );
}
