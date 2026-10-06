import { clsx, type ClassValue } from "clsx";

/**
 * Join class names. Primitives put their defaults first and the caller's
 * `className` last; overrides that must win use `!` or a more specific class.
 */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}
