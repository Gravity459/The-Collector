import type { Transition, Variants } from "motion/react";

/**
 * Shared motion presets. Motion only conveys state change (selection,
 * rows entering/leaving, dialogs, values ticking, views switching); never
 * decoration. Exits are faster than entrances. Reduced motion is honoured
 * globally via <MotionConfig reducedMotion="user"> (transforms dropped,
 * opacity kept).
 */

/** Exponential ease-out. */
export const ease = [0.16, 1, 0.3, 1] as const;

/** Layout moves: active nav pill, segmented thumb, rows reflowing. */
export const spring: Transition = { type: "spring", stiffness: 500, damping: 40 };

export const fade: Transition = { duration: 0.18, ease };

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: fade },
  exit: { opacity: 0, transition: { duration: 0.12, ease } },
};

export const dialog: Variants = {
  initial: { opacity: 0, scale: 0.97, y: 6 },
  animate: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.24, ease } },
  exit: { opacity: 0, scale: 0.98, y: 4, transition: { duration: 0.14, ease } },
};

export const sheet: Variants = {
  initial: { y: "100%" },
  animate: { y: 0, transition: { duration: 0.32, ease } },
  exit: { y: "100%", transition: { duration: 0.2, ease } },
};

/** A result set arriving: the container settles from the old page's dim, rows stagger. */
export const list: Variants = {
  initial: { opacity: 0.5 },
  animate: {
    opacity: 1,
    transition: { duration: 0.2, ease, staggerChildren: 0.025, delayChildren: 0.02 },
  },
};

/** One row: rises in as part of a list; slides out sideways when removed. */
export const row: Variants = {
  initial: { opacity: 0, y: 4 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.22, ease } },
  exit: { opacity: 0, x: 24, transition: { duration: 0.18, ease } },
};

/** Route content entering. */
export const page: Variants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.26, ease } },
};
