interface Props {
  page: number;
  totalPages: number;
  onChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onChange }: Props) {
  const canPrev = page > 1;
  const canNext = page < totalPages;
  const btn =
    "rounded-lg border border-zinc-300 px-3 py-1.5 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100 disabled:opacity-40 disabled:hover:bg-transparent dark:border-zinc-700 dark:text-zinc-200 dark:hover:bg-zinc-800";

  return (
    <div className="flex items-center justify-between gap-3 border-t border-zinc-200 px-4 py-3 dark:border-zinc-800">
      <span className="text-sm text-zinc-500 dark:text-zinc-400">
        Page {totalPages === 0 ? 0 : page} of {totalPages}
      </span>
      <div className="flex gap-2">
        <button
          onClick={() => canPrev && onChange(page - 1)}
          disabled={!canPrev}
          className={btn}
        >
          Previous
        </button>
        <button
          onClick={() => canNext && onChange(page + 1)}
          disabled={!canNext}
          className={btn}
        >
          Next
        </button>
      </div>
    </div>
  );
}
