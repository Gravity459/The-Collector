"use client";

import { AdminView } from "@/components/AdminView";
import { Spinner } from "@/components/Spinner";
import { UserView } from "@/components/UserView";
import { useMe } from "@/lib/queries";

export default function OverviewPage() {
  const { data: me, isLoading, isError } = useMe();

  if (isLoading) {
    return <Spinner size="lg" label="Loading…" center />;
  }
  if (isError || !me) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">
        Could not load your profile. Try signing in again.
      </p>
    );
  }

  return me.role === "admin" ? <AdminView /> : <UserView />;
}
