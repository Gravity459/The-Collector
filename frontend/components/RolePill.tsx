import type { Role } from "@/lib/types";

import { Pill } from "./ui/Pill";

const ROLE: Record<Role, { label: string; tone: string; bg: string }> = {
  admin: { label: "Admin", tone: "text-role-admin", bg: "bg-role-admin-bg" },
  collector: {
    label: "Collector",
    tone: "text-role-collector",
    bg: "bg-role-collector-bg",
  },
  user: { label: "User", tone: "text-role-user", bg: "bg-role-user-bg" },
};

/** Role pill: violet admin, sky collector, amber user. */
export function RolePill({ role, className }: { role: Role; className?: string }) {
  const r = ROLE[role];
  return (
    <Pill tone={r.tone} bg={r.bg} className={className}>
      {r.label}
    </Pill>
  );
}
