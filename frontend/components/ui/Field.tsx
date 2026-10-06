"use client";

import { cloneElement, isValidElement, useId } from "react";

import { cn } from "@/lib/cn";

interface Props {
  label: string;
  error?: string;
  hint?: string;
  className?: string;
  /** A single form control; receives id, aria-describedby and invalid. */
  children: React.ReactElement<{
    id?: string;
    invalid?: boolean;
    "aria-describedby"?: string;
  }>;
}

/** Label + control + error/hint line, wired for screen readers. */
export function Field({ label, error, hint, className, children }: Props) {
  const id = useId();
  const messageId = `${id}-msg`;
  const message = error ?? hint;

  const control = isValidElement(children)
    ? cloneElement(children, {
        id,
        invalid: Boolean(error),
        "aria-describedby": message ? messageId : undefined,
      })
    : children;

  return (
    <div className={cn("min-w-0", className)}>
      <label htmlFor={id} className="mb-1.5 block text-xs font-medium text-fg-muted">
        {label}
      </label>
      {control}
      {message && (
        <p
          id={messageId}
          role={error ? "alert" : undefined}
          className={cn("mt-1.5 text-xs", error ? "text-danger" : "text-fg-subtle")}
        >
          {message}
        </p>
      )}
    </div>
  );
}
