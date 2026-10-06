"use client";

import * as m from "motion/react-m";

import { PageSkeleton } from "@/components/PageSkeleton";
import { UsersView } from "@/components/UsersView";
import { fadeIn } from "@/lib/motion";
import { useMe } from "@/lib/queries";

export default function UsersPage() {
  const { data: me, isLoading, isError } = useMe();

  if (isLoading) return <PageSkeleton kpis={false} />;
  if (isError || !me) {
    return (
      <p role="alert" className="text-sm text-danger">
        Your profile couldn&apos;t be loaded. Sign out and sign in again.
      </p>
    );
  }
  // presentation only: the backend enforces admin on every /users call
  if (me.role !== "admin") {
    return (
      <p className="text-sm text-fg-muted">
        Only admins can manage users.
      </p>
    );
  }

  return (
    <m.div variants={fadeIn} initial="initial" animate="animate">
      <UsersView />
    </m.div>
  );
}
