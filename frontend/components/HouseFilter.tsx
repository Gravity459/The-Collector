"use client";

import { useState } from "react";

interface Props {
  value: number | null;
  onChange: (houseNumber: number | null) => void;
}

export function HouseFilter({ value, onChange }: Props) {
  const [draft, setDraft] = useState<string>(value != null ? String(value) : "");

  function apply() {
    const trimmed = draft.trim();
    onChange(trimmed === "" ? null : Number(trimmed));
  }

  const input =
    "w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 outline-none transition placeholder:text-zinc-400 focus:border-accent focus:ring-2 focus:ring-accent/30 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100";

  return (
    <div className="flex w-full flex-wrap items-end gap-2 sm:w-auto">
      <div className="flex-1 sm:flex-none">
        <label className="mb-1 block text-xs font-medium text-zinc-500 dark:text-zinc-400">
          House number
        </label>
        <input
          type="number"
          inputMode="numeric"
          min={1}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && apply()}
          placeholder="All"
          className={`${input} sm:w-32`}
        />
      </div>
      <button
        onClick={apply}
        className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition hover:bg-accent-hover"
      >
        Filter
      </button>
      {value != null && (
        <button
          onClick={() => {
            setDraft("");
            onChange(null);
          }}
          className="rounded-lg border border-zinc-300 px-3 py-2 text-sm text-zinc-600 transition hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
        >
          Clear
        </button>
      )}
    </div>
  );
}
