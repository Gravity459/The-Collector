"use client";

import * as m from "motion/react-m";

import { page } from "@/lib/motion";

/** Re-mounts on every dashboard navigation: content settles in instead of snapping. */
export default function DashboardTemplate({ children }: { children: React.ReactNode }) {
  return (
    <m.div variants={page} initial="initial" animate="animate">
      {children}
    </m.div>
  );
}
