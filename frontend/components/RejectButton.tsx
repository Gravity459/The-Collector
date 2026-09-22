"use client";

import { useState } from "react";

import { useDeleteCollection } from "@/lib/queries";

import { ConfirmModal } from "./ConfirmModal";

export function RejectButton({
  id,
  houseNumber,
}: {
  id: string;
  houseNumber: number;
}) {
  const [open, setOpen] = useState(false);
  const reject = useDeleteCollection();

  function confirm() {
    reject.mutate(id, { onSuccess: () => setOpen(false) });
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
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
        Reject
      </button>

      <ConfirmModal
        open={open}
        title="Reject collection"
        message={`This will permanently delete the pending collection for house S-${houseNumber}. This action cannot be undone.`}
        confirmLabel="Reject"
        loading={reject.isPending}
        onConfirm={confirm}
        onCancel={() => setOpen(false)}
      />
    </>
  );
}
