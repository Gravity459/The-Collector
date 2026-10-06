"use client";

import * as m from "motion/react-m";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/cn";
import { spring } from "@/lib/motion";

import { useNav } from "./Sidebar";

/** Phone tab bar. Hidden when there is only one destination. */
export function BottomNav() {
  const pathname = usePathname();
  const nav = useNav();
  if (nav.length < 2) return null;

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-bg/90 pb-[env(safe-area-inset-bottom)] backdrop-blur-md md:hidden"
    >
      <ul className="mx-auto flex max-w-md">
        {nav.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <li key={item.href} className="flex-1">
              <Link
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "relative flex h-14 flex-col items-center justify-center gap-1 text-xs font-medium transition-colors",
                  active ? "text-fg" : "text-fg-subtle",
                )}
              >
                {active && (
                  <m.span
                    layoutId="bottom-active"
                    transition={spring}
                    className="absolute inset-x-6 top-0 h-0.5 rounded-full bg-fg"
                  />
                )}
                <Icon className="h-5 w-5" aria-hidden />
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
