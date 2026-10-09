export type Role = "user" | "admin" | "collector";

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  created_at: string;
  updated_at: string;
}

export type SheetSyncStatus = "pending" | "done" | "needs_review" | "failed";
export type SheetSyncReason =
  | "conflict"
  | "house_not_in_sheet"
  | "month_column_missing"
  | "layout_unreadable";

/** Where an approved payment stands in the Google Sheet. */
export interface SheetSyncSummary {
  status: SheetSyncStatus;
  reason: SheetSyncReason | null;
  target_cell: string | null;
}

export interface SheetSyncJob {
  id: string;
  collection_id: string;
  house_number: number;
  period_month: string;
  amount: number;
  status: SheetSyncStatus;
  reason: SheetSyncReason | null;
  target_cell: string | null;
  existing_value: string | null;
  error: string | null;
  attempts: number;
  updated_at: string;
}

export interface Collection {
  id: string;
  house_id: string;
  house_number: number;
  amount: number;
  /** Month the payment is for, "YYYY-MM" (may differ from created_at). */
  period_month: string;
  approved: boolean;
  collector_name: string | null;
  /** Null unless approved while sheet sync was on. */
  sheet_sync: SheetSyncSummary | null;
  created_at: string;
  updated_at: string;
}

export interface CollectionTotal {
  total: number;
}

export interface Page<T> {
  items: T[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
}

export const COOKIE_NAME = "access_token";

/** Desktop sidebar pinned open ("1") or collapsed to the rail. Read server-side to avoid a layout shift. */
export const PIN_COOKIE = "sidebar-pinned";
