"use client";

import { useEffect, useState } from "react";

/**
 * True while the media query matches. By default false during SSR and the
 * first render (hydration-safe). Pass `sync` for components that only ever
 * mount on the client after an interaction (e.g. dialogs), so their first
 * frame already uses the right layout.
 */
export function useMediaQuery(query: string, { sync = false } = {}): boolean {
  const [matches, setMatches] = useState(() =>
    sync && typeof window !== "undefined" ? window.matchMedia(query).matches : false,
  );
  useEffect(() => {
    const mq = window.matchMedia(query);
    const update = () => setMatches(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, [query]);
  return matches;
}

/** Below Tailwind's `sm` breakpoint. */
export const PHONE_QUERY = "(max-width: 639px)";
