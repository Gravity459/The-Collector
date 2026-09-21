"use client";

import { useApproveCollection } from "@/lib/queries";

export function ApproveButton({ id }: { id: string }) {
  const approve = useApproveCollection();
  return (
    <button
      onClick={() => approve.mutate(id)}
      disabled={approve.isPending}
      className="inline-flex items-center gap-1.5 rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-green-700 disabled:opacity-60"
    >
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M20 6 9 17l-5-5" />
      </svg>
      {approve.isPending ? "Approving…" : "Approve"}
    </button>
  );
}
