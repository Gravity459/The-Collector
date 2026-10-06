"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { AnimatePresence } from "motion/react";
import * as m from "motion/react-m";
import { useRef, useState } from "react";

import { currentMonth, formatMonth, shiftMonth } from "@/lib/format";
import { ease } from "@/lib/motion";

import { Button } from "./ui/Button";

interface Props {
  value: string;
  onChange: (month: string) => void;
}

/** "‹ October 2026 ›" stepper. The label opens the native month picker. */
export function MonthFilter({ value, onChange }: Props) {
  const max = currentMonth();
  const picker = useRef<HTMLInputElement>(null);
  const atMax = value >= max;
  // label slides the way the month moved: later months come from the right
  const [shown, setShown] = useState(value);
  const [dir, setDir] = useState(0);
  if (value !== shown) {
    setShown(value);
    setDir(value > shown ? 1 : -1);
  }

  function openPicker() {
    const el = picker.current;
    if (!el) return;
    try {
      el.showPicker();
    } catch {
      el.focus();
    }
  }

  return (
    <div className="flex h-9 w-full items-center rounded-control border border-border-strong bg-surface sm:inline-flex sm:w-auto">
      <Button
        variant="ghost"
        size="icon"
        aria-label="Previous month"
        className="!h-full !w-8 rounded-r-none"
        onClick={() => onChange(shiftMonth(value, -1))}
      >
        <ChevronLeft className="h-4 w-4" aria-hidden />
      </Button>
      <div className="relative h-full flex-1 sm:flex-none">
        <button
          type="button"
          onClick={openPicker}
          aria-label={`Month: ${formatMonth(value)}. Choose month`}
          className="relative h-full w-full min-w-[8.5rem] overflow-hidden px-2 text-center text-sm font-medium tabular-nums text-fg transition-colors hover:bg-surface-2"
        >
          <AnimatePresence mode="popLayout" initial={false} custom={dir}>
            <m.span
              key={value}
              custom={dir}
              initial={{ opacity: 0, x: dir * 10 }}
              animate={{ opacity: 1, x: 0, transition: { duration: 0.2, ease } }}
              exit={{ opacity: 0, x: dir * -10, transition: { duration: 0.12, ease } }}
              className="block"
            >
              {formatMonth(value)}
            </m.span>
          </AnimatePresence>
        </button>
        <input
          ref={picker}
          type="month"
          tabIndex={-1}
          aria-hidden
          value={value}
          max={max}
          // clearing the native picker yields "": fall back to the current month
          onChange={(e) => onChange(e.target.value || max)}
          className="pointer-events-none absolute inset-0 opacity-0"
        />
      </div>
      <Button
        variant="ghost"
        size="icon"
        aria-label="Next month"
        className="!h-full !w-8 rounded-l-none"
        disabled={atMax}
        onClick={() => onChange(shiftMonth(value, 1))}
      >
        <ChevronRight className="h-4 w-4" aria-hidden />
      </Button>
    </div>
  );
}
