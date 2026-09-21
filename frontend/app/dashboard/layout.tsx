import { redirect } from "next/navigation";

import { Sidebar } from "@/components/Sidebar";
import { Topbar } from "@/components/Topbar";
import { getToken } from "@/lib/server";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  if (!(await getToken())) redirect("/login");

  return (
    <div className="md:flex md:min-h-screen">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <Topbar />
        <main className="mx-auto w-full max-w-5xl flex-1 p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
