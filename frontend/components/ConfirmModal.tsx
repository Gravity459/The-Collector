"use client";

import { useEffect } from "react";

interface Props {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  loadingLabel?: string;
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmModal({
  open,
  title,
  message,
  confirmLabel = "Remove",
  cancelLabel = "Cancel",
  loadingLabel,
  loading = false,
  onConfirm,
  onCancel,
}: Props) {
  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onCancel();
    }
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 animate-fade-in"
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="relative w-full max-w-sm rounded-3xl border border-zinc-200 bg-white p-8 shadow-xl animate-scale-in dark:border-zinc-800 dark:bg-zinc-900"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onCancel}
          disabled={loading}
          aria-label="Close"
          className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-zinc-400 transition hover:bg-zinc-100 hover:text-zinc-600 disabled:opacity-60 dark:hover:bg-zinc-800 dark:hover:text-zinc-300"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>

        <div className="flex flex-col items-center text-center">
          <span className="flex h-14 w-14 items-center justify-center rounded-full bg-red-100 text-red-600 dark:bg-red-500/15 dark:text-red-400">
            <svg
              width="26"
              height="26"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 8v5M12 16h.01" />
            </svg>
          </span>
          <h3 className="mt-5 text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
            {title}
          </h3>
          <p className="mt-3 text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
            {message}
          </p>
        </div>

        <div className="mt-8 grid grid-cols-2 gap-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="rounded-xl bg-zinc-100 px-4 py-3 text-sm font-semibold text-zinc-800 transition hover:bg-zinc-200 disabled:opacity-60 dark:bg-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-700"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="rounded-xl bg-red-500 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-red-600 disabled:opacity-60"
          >
            {loading ? loadingLabel ?? `${confirmLabel}…` : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
