import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { BottomNav } from "@/components/BottomNav";
import { Sidebar } from "@/components/Sidebar";
import { Topbar } from "@/components/Topbar";
import { getToken } from "@/lib/server";
import { PIN_COOKIE } from "@/lib/types";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  if (!(await getToken())) redirect("/login");
  const pinned = (await cookies()).get(PIN_COOKIE)?.value === "1";

  return (
    <div className="md:flex md:min-h-screen">
      <a
        href="#main"
        className="sr-only z-50 rounded-control bg-fg px-3 py-2 text-sm font-medium text-on-fg focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        Skip to content
      </a>
      <Sidebar initialPinned={pinned} />
      <div className="flex min-h-screen min-w-0 flex-1 flex-col">
        <Topbar />
        <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-4 pb-24 pt-5 sm:px-6 md:px-8 md:pb-10 md:pt-8">
          {children}
        </main>
        <BottomNav />
      </div>
    </div>
  );
}
