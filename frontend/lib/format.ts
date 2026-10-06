/** Display currency for every amount in the app. */
export const CURRENCY = "PKR";

const amountFormat = new Intl.NumberFormat("en-PK", {
  maximumFractionDigits: 0,
});

/** Mandatory house label: 14 -> "S-14". */
export function houseLabel(houseNumber: number): string {
  return `S-${houseNumber}`;
}

/** 5000 -> "PKR 5,000" */
export function formatAmount(amount: number): string {
  return `${CURRENCY} ${amountFormat.format(amount)}`;
}

/** 5000 -> "5,000" (when the currency is shown separately). */
export function formatNumber(n: number): string {
  return amountFormat.format(n);
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** "just now", "5m ago", "2h ago", "3d ago", then a short date after a week. */
export function relativeTime(iso: string, now: number = Date.now()): string {
  const seconds = Math.round((now - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/** Current month as "YYYY-MM" (local time). */
export function currentMonth(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

/** "2026-10" -> "October 2026" */
export function formatMonth(month: string): string {
  const [y, m] = month.split("-").map(Number);
  return new Date(y, m - 1).toLocaleString(undefined, {
    month: "long",
    year: "numeric",
  });
}

/** "2026-10" -> "October" */
export function formatMonthName(month: string): string {
  const [y, m] = month.split("-").map(Number);
  return new Date(y, m - 1).toLocaleString(undefined, { month: "long" });
}

/** shiftMonth("2026-01", -1) -> "2025-12" */
export function shiftMonth(month: string, delta: number): string {
  const [y, m] = month.split("-").map(Number);
  const d = new Date(y, m - 1 + delta);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

/** "Imran Khan" -> "IK" */
export function initials(name: string): string {
  return (
    name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((p) => p[0]?.toUpperCase() ?? "")
      .join("") || "?"
  );
}
