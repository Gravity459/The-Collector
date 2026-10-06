"use client";

import { useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";

interface Props {
  value: number;
  /** Formats each frame; defaults to a grouped integer. */
  format?: (n: number) => string;
  className?: string;
}

const defaultFormat = (n: number) => Math.round(n).toLocaleString("en-PK");
const DURATION = 500;
/** Exponential ease-out, matching lib/motion `ease`. */
const easeOut = (t: number) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t));

/**
 * A number that ticks from its previous value to the new one when it changes
 * (the approval hand-off). The first render shows the value as-is: no
 * count-up on page load. A small rAF tween keeps the Motion engine out of
 * the first-load bundle.
 */
export function AnimatedNumber({ value, format = defaultFormat, className }: Props) {
  const [display, setDisplay] = useState(value);
  const current = useRef(value);
  const reduce = useReducedMotion();

  useEffect(() => {
    const from = current.current;
    if (from === value) return;
    if (reduce) {
      current.current = value;
      setDisplay(value);
      return;
    }
    let frame = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / DURATION);
      const n = from + (value - from) * easeOut(t);
      current.current = n;
      setDisplay(n);
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value, reduce]);

  return <span className={className}>{format(display)}</span>;
}
