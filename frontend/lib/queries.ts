"use client";

import {
  keepPreviousData,
  type QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import axios from "axios";
import { toast } from "sonner";

import { api } from "./api";
import { houseLabel } from "./format";
import type { Collection, CollectionTotal, Page, Role, User } from "./types";

/** Backend error `detail` (string, or FastAPI's 422 list) with a fallback. */
export function errorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && typeof detail[0]?.msg === "string") {
      return detail[0].msg;
    }
  }
  return fallback;
}

/** Shared onError: every mutation reports failures as a toast. */
function toastError(fallback: string) {
  return (error: unknown) => {
    toast.error(errorMessage(error, fallback));
  };
}

export interface CollectionFilters {
  page?: number;
  size?: number;
  house_number?: number | null;
  approved?: boolean | null;
  /** "YYYY-MM" */
  month?: string | null;
}

export function useMe() {
  return useQuery<User>({
    queryKey: ["me"],
    queryFn: async () => (await api.get<User>("/me")).data,
    retry: false,
  });
}

export function useCollections(filters: CollectionFilters) {
  const { page = 1, size = 10, house_number, approved, month } = filters;
  return useQuery<Page<Collection>>({
    queryKey: ["collections", { page, size, house_number, approved, month }],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, size };
      if (house_number != null) params.house_number = house_number;
      if (approved != null) params.approved = String(approved);
      if (month) params.month = month;
      return (await api.get<Page<Collection>>("/collections", { params })).data;
    },
    // keep the previous page on screen while the next one loads (no skeleton flash)
    placeholderData: keepPreviousData,
  });
}

export function useCollectionTotal({
  approved,
  month,
}: {
  approved: boolean;
  month?: string | null;
}) {
  return useQuery<CollectionTotal>({
    queryKey: ["collections", "total", { approved, month }],
    queryFn: async () => {
      const params: Record<string, string> = { approved: String(approved) };
      if (month) params.month = month;
      return (await api.get<CollectionTotal>("/collections/total", { params })).data;
    },
    // lets the KPI tick from the old month's value to the new one
    placeholderData: keepPreviousData,
  });
}

export function useCreateCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: { house_number: number; amount: number }) =>
      (await api.post<Collection>("/collections", body)).data,
    onSuccess: (c) => {
      qc.invalidateQueries({ queryKey: ["collections"] });
      toast.success(`Collection for ${houseLabel(c.house_number)} submitted`);
    },
    onError: toastError(
      "Could not submit the collection. Check the values and try again.",
    ),
  });
}

type TotalKey = readonly [
  "collections",
  "total",
  { approved: boolean; month?: string | null },
];
type ListKey = readonly ["collections", CollectionFilters];

/** "YYYY-MM" of a timestamp; the backend's month filter keys on created_at. */
function monthOf(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

/** Add `delta` to every cached total matching `match`. */
function bumpTotals(qc: QueryClient, match: (f: TotalKey[2]) => boolean, delta: number) {
  for (const [key, data] of qc.getQueriesData<CollectionTotal>({
    queryKey: ["collections", "total"],
  })) {
    const f = (key as unknown as TotalKey)[2];
    if (data && f && match(f)) {
      qc.setQueryData<CollectionTotal>(key, { total: Math.max(0, data.total + delta) });
    }
  }
}

/**
 * Optimistic update for approve / reject / remove so the whole hand-off moves
 * at once: the row leaves its list, list counts and money totals adjust.
 * Returns a snapshot of every collections query for rollback.
 */
async function applyOptimistic(
  qc: QueryClient,
  c: Collection,
  action: "approve" | "delete",
) {
  await qc.cancelQueries({ queryKey: ["collections"] });
  const snapshot = qc.getQueriesData({ queryKey: ["collections"] });
  const month = monthOf(c.created_at);

  // 1. the row leaves every list it is in
  qc.setQueriesData<Page<Collection>>({ queryKey: ["collections"] }, (old) => {
    if (!old || !Array.isArray(old.items)) return old;
    if (!old.items.some((x) => x.id === c.id)) return old;
    return {
      ...old,
      items: old.items.filter((x) => x.id !== c.id),
      total: Math.max(0, old.total - 1),
    };
  });

  // 2. money moves with it
  const sign = c.approved ? { approved: true, month } : { approved: false };
  bumpTotals(
    qc,
    (f) => f.approved === sign.approved && (!sign.approved || f.month === month),
    -c.amount,
  );
  if (action === "approve") {
    bumpTotals(qc, (f) => f.approved && f.month === month, c.amount);
    // 3. the Approved list for that month gains one (row arrives on refetch)
    for (const [key, data] of qc.getQueriesData<Page<Collection>>({
      queryKey: ["collections"],
    })) {
      const f = (key as unknown as ListKey)[1];
      if (
        data &&
        Array.isArray(data.items) &&
        typeof f === "object" &&
        f.approved === true &&
        f.month === month &&
        (f.house_number == null || f.house_number === c.house_number)
      ) {
        qc.setQueryData<Page<Collection>>(key, { ...data, total: data.total + 1 });
      }
    }
  }
  return snapshot;
}

type Snapshot = Awaited<ReturnType<typeof applyOptimistic>>;

function restore(qc: QueryClient, snapshot: Snapshot | undefined) {
  snapshot?.forEach(([key, data]) => qc.setQueryData(key, data));
}

export function useApproveCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (c: Collection) =>
      (await api.patch<Collection>(`/collections/${c.id}/approve`)).data,
    onMutate: (c) => applyOptimistic(qc, c, "approve"),
    onSuccess: (c) => {
      toast.success(`Collection for ${houseLabel(c.house_number)} approved`);
    },
    onError: (error, _c, snapshot) => {
      restore(qc, snapshot);
      toastError("Could not approve the collection. Try again.")(error);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["collections"] }),
  });
}

/**
 * Reject (pending) or remove (approved) a collection. The success toast is
 * passed in because the row (and its button) has already unmounted by then.
 */
export function useDeleteCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      collection,
    }: {
      collection: Collection;
      successMessage: string;
    }) => {
      await api.delete(`/collections/${collection.id}`);
    },
    onMutate: ({ collection }) => applyOptimistic(qc, collection, "delete"),
    onSuccess: (_data, { successMessage }) => {
      toast.success(successMessage);
    },
    onError: (error, _vars, snapshot) => {
      restore(qc, snapshot);
      toastError("Could not delete the collection. Try again.")(error);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["collections"] }),
  });
}

export function useUsers(page: number) {
  return useQuery<Page<User>>({
    queryKey: ["users", { page }],
    queryFn: async () =>
      (await api.get<Page<User>>("/users", { params: { page, size: 10 } })).data,
    placeholderData: keepPreviousData,
  });
}

export function useCreateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: {
      name: string;
      email: string;
      password: string;
      role: Role;
    }) => (await api.post<User>("/users", body)).data,
    onSuccess: (u) => {
      qc.invalidateQueries({ queryKey: ["users"] });
      toast.success(`User ${u.email} created`);
    },
    onError: toastError("Could not create the user."),
  });
}

export function useUpdateUserPassword() {
  return useMutation({
    mutationFn: async ({ id, password }: { id: string; password: string }) => {
      await api.patch(`/users/${id}/password`, { password });
    },
    onSuccess: () => {
      toast.success("Password updated");
    },
    onError: toastError("Could not update the password."),
  });
}

export function useDeleteUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/users/${id}`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] });
      // collector emails on existing rows become null
      qc.invalidateQueries({ queryKey: ["collections"] });
    },
    // success toast is set by the caller (knows the email)
    onError: toastError("Could not remove the user."),
  });
}
