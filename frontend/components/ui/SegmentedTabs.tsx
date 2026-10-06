"use client";

import * as m from "motion/react-m";
import { useId, useRef } from "react";

import { cn } from "@/lib/cn";
import { spring } from "@/lib/motion";

import { AnimatedNumber } from "./AnimatedNumber";

export interface SegmentedItem<T extends string> {
  value: T;
  label: string;
  count?: number;
}

interface Props<T extends string> {
  value: T;
  onChange: (value: T) => void;
  items: SegmentedItem<T>[];
  /** Accessible name for the tab list. */
  label: string;
  /** id prefix for aria-controls; panels use `${idBase}-panel-${value}`. */
  idBase: string;
}

/** Tabs with a sliding thumb. Arrow keys move between tabs (roving tabindex). */
export function SegmentedTabs<T extends string>({
  value,
  onChange,
  items,
  label,
  idBase,
}: Props<T>) {
  const layoutId = useId();
  const refs = useRef<(HTMLButtonElement | null)[]>([]);

  function onKeyDown(e: React.KeyboardEvent, index: number) {
    let next = -1;
    if (e.key === "ArrowRight") next = (index + 1) % items.length;
    if (e.key === "ArrowLeft") next = (index - 1 + items.length) % items.length;
    if (e.key === "Home") next = 0;
    if (e.key === "End") next = items.length - 1;
    if (next < 0) return;
    e.preventDefault();
    onChange(items[next].value);
    refs.current[next]?.focus();
  }

  return (
    <div
      role="tablist"
      aria-label={label}
      className="inline-flex h-8 w-fit shrink-0 items-center gap-0.5 self-start rounded-control border border-border bg-bg p-0.5 sm:self-auto"
    >
      {items.map((item, i) => {
        const selected = item.value === value;
        return (
          <button
            key={item.value}
            ref={(el) => {
              refs.current[i] = el;
            }}
            id={`${idBase}-tab-${item.value}`}
            role="tab"
            type="button"
            aria-selected={selected}
            aria-controls={`${idBase}-panel-${item.value}`}
            tabIndex={selected ? 0 : -1}
            onClick={() => onChange(item.value)}
            onKeyDown={(e) => onKeyDown(e, i)}
            className={cn(
              "relative inline-flex h-full items-center gap-1.5 rounded-[5px] px-3 text-sm font-medium transition-colors duration-150",
              selected ? "text-fg" : "text-fg-muted hover:text-fg",
            )}
          >
            {selected && (
              <m.span
                layoutId={layoutId}
                transition={spring}
                className="absolute inset-0 rounded-[5px] bg-surface-2 shadow-[inset_0_0_0_1px_rgb(var(--border-strong))]"
              />
            )}
            <span className="relative">{item.label}</span>{" "}
            {item.count != null && (
              <AnimatedNumber
                value={item.count}
                className="relative text-xs tabular-nums text-fg-subtle"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
