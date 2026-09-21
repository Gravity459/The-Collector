"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { LogoutButton } from "./LogoutButton";
import { ThemeToggle } from "./ThemeToggle";

const NAV = [{ label: "Overview", href: "/dashboard/overview" }];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-zinc-200 bg-white md:flex dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between px-6 py-5">
        <span className="text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
          The Collector
        </span>
        <ThemeToggle />
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {NAV.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-lg px-3 py-2 text-sm font-medium transition ${
                active
                  ? "bg-accent text-white shadow-sm"
                  : "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-zinc-200 p-3 dark:border-zinc-800">
        <LogoutButton />
      </div>
    </aside>
  );
}
