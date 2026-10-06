import { cn } from "@/lib/cn";

/** The Collector mark on its own: a ledger square with ruled lines. */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
      className={cn("shrink-0 text-fg", className)}
    >
      <rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" strokeWidth="1.75" />
      <path d="M8 10h8M8 14h5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

/** Mark + wordmark. */
export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("flex items-center gap-2.5", className)}>
      <LogoMark />
      <span translate="no" className="text-sm font-semibold tracking-tight text-fg">
        The Collector
      </span>
    </span>
  );
}
