"use client";

import { X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "./ui/Button";
import { Input } from "./ui/Input";

interface Props {
  value: number | null;
  onChange: (houseNumber: number | null) => void;
}

/** "S-" prefixed house search. Applies 300ms after typing stops. */
export function HouseFilter({ value, onChange }: Props) {
  const [draft, setDraft] = useState<string>(value != null ? String(value) : "");
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;
  const applied = useRef(value);

  useEffect(() => {
    const trimmed = draft.trim();
    const next = trimmed === "" ? null : Number(trimmed);
    if (next !== null && (!Number.isInteger(next) || next < 1)) return;
    if (next === applied.current) return;
    const t = setTimeout(() => {
      applied.current = next;
      onChangeRef.current(next);
    }, 300);
    return () => clearTimeout(t);
  }, [draft]);

  return (
    <Input
      type="number"
      inputMode="numeric"
      min={1}
      aria-label="Filter by house number"
      placeholder="All houses"
      prefix="S-"
      value={draft}
      onChange={(e) => setDraft(e.target.value)}
      className="w-full sm:w-40"
      trailing={
        draft !== "" ? (
          <Button
            key="clear"
            variant="ghost"
            size="icon-sm"
            aria-label="Clear house filter"
            className="!h-6 !w-6 motion-safe:animate-[pop-in_150ms_cubic-bezier(0.16,1,0.3,1)]"
            onClick={() => setDraft("")}
          >
            <X className="h-3.5 w-3.5" aria-hidden />
          </Button>
        ) : undefined
      }
    />
  );
}
