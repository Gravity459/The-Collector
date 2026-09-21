"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "./api";
import type { Collection, Page, User } from "./types";

export interface CollectionFilters {
  page?: number;
  size?: number;
  house_number?: number | null;
  approved?: boolean | null;
}

export function useMe() {
  return useQuery<User>({
    queryKey: ["me"],
    queryFn: async () => (await api.get<User>("/me")).data,
    retry: false,
  });
}

export function useCollections(filters: CollectionFilters) {
  const { page = 1, size = 10, house_number, approved } = filters;
  return useQuery<Page<Collection>>({
    queryKey: ["collections", { page, size, house_number, approved }],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, size };
      if (house_number != null) params.house_number = house_number;
      if (approved != null) params.approved = String(approved);
      return (await api.get<Page<Collection>>("/collections", { params })).data;
    },
  });
}

export function useCreateCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: { house_number: number; amount: number }) =>
      (await api.post<Collection>("/collections", body)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["collections"] });
    },
  });
}

export function useApproveCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) =>
      (await api.patch<Collection>(`/collections/${id}/approve`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["collections"] });
    },
  });
}

export function useDeleteCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/collections/${id}`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["collections"] });
    },
  });
}
