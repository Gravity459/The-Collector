"use client";

import { useEffect, useState } from "react";

/** True while the media query matches. False during SSR and the first render. */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);
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
