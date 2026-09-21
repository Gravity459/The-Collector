"use client";

import { useState } from "react";

import { useDeleteCollection } from "@/lib/queries";

import { ConfirmModal } from "./ConfirmModal";

export function RemoveButton({
  id,
  houseNumber,
}: {
  id: string;
  houseNumber: number;
}) {
  const [open, setOpen] = useState(false);
  const remove = useDeleteCollection();

  function confirm() {
    remove.mutate(id, { onSuccess: () => setOpen(false) });
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1.5 rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-50 dark:border-red-500/30 dark:text-red-400 dark:hover:bg-red-500/10"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
        </svg>
        Remove
      </button>

      <ConfirmModal
        open={open}
        title="Remove approved payment"
        message={`This will permanently remove the approved payment for house S-${houseNumber}. This action cannot be undone.`}
        confirmLabel="Remove"
        loading={remove.isPending}
        onConfirm={confirm}
        onCancel={() => setOpen(false)}
      />
    </>
  );
}
