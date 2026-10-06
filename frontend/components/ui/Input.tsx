import { forwardRef } from "react";

import { cn } from "@/lib/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Fixed text shown inside the field before the value, e.g. "S-" or "PKR". */
  prefix?: string;
  /** Element pinned to the right edge (e.g. a clear button). */
  trailing?: React.ReactNode;
  /** Larger, touch-friendly height (44px). */
  touch?: boolean;
  invalid?: boolean;
}

const base =
  "w-full rounded-control border bg-surface text-fg outline-none transition-[border-color,box-shadow] duration-150 placeholder:text-fg-subtle focus:ring-2 disabled:cursor-not-allowed disabled:opacity-50";

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { prefix, trailing, touch, invalid, className, ...props },
  ref,
) {
  return (
    <div className={cn("relative flex items-center", className)}>
      {prefix && (
        <span
          aria-hidden
          className="pointer-events-none absolute left-3 select-none text-sm font-medium text-fg-subtle"
        >
          {prefix}
        </span>
      )}
      <input
        ref={ref}
        aria-invalid={invalid || undefined}
        className={cn(
          base,
          touch ? "h-11 text-md sm:h-9 sm:text-sm" : "h-9 text-sm",
          prefix ? (prefix.length > 2 ? "pl-12" : "pl-8") : "pl-3",
          trailing ? "pr-9" : "pr-3",
          invalid
            ? "border-danger/60 focus:border-danger focus:ring-danger/15"
            : "border-border-strong focus:border-fg/40 focus:ring-fg/10",
        )}
        {...props}
      />
      {trailing && <span className="absolute right-1.5">{trailing}</span>}
    </div>
  );
});

export const Select = forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement> & { invalid?: boolean }
>(function Select({ className, invalid, children, ...props }, ref) {
  return (
    <div className={cn("relative", className)}>
      <select
        ref={ref}
        aria-invalid={invalid || undefined}
        className={cn(
          base,
          "h-9 cursor-pointer appearance-none pl-3 pr-9 text-sm",
          invalid
            ? "border-danger/60 focus:border-danger focus:ring-danger/15"
            : "border-border-strong focus:border-fg/40 focus:ring-fg/10",
        )}
        {...props}
      >
        {children}
      </select>
      <svg
        aria-hidden="true"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-fg-subtle"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </div>
  );
});
