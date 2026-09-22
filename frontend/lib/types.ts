export type Role = "user" | "admin";

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  created_at: string;
  updated_at: string;
}

export interface Collection {
  id: string;
  house_id: string;
  house_number: number;
  amount: number;
  approved: boolean;
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
