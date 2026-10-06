"use client";

import * as m from "motion/react-m";

import { AdminView } from "@/components/AdminView";
import { PageSkeleton } from "@/components/PageSkeleton";
import { UserView } from "@/components/UserView";
import { fadeIn } from "@/lib/motion";
import { useMe } from "@/lib/queries";

export default function OverviewPage() {
  const { data: me, isLoading, isError } = useMe();

  if (isLoading) return <PageSkeleton />;
  if (isError || !me) {
    return (
      <p role="alert" className="text-sm text-danger">
        Your profile couldn&apos;t be loaded. Sign out and sign in again.
      </p>
    );
  }

  return (
    <m.div variants={fadeIn} initial="initial" animate="animate">
      {me.role === "admin" ? <AdminView /> : <UserView role={me.role} />}
    </m.div>
  );
}
