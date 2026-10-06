"use client";

import {
  LayoutDashboard,
  type LucideIcon,
  PanelLeftClose,
  PanelLeftOpen,
  Users,
} from "lucide-react";
import { AnimatePresence, useReducedMotion } from "motion/react";
import * as m from "motion/react-m";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { cn } from "@/lib/cn";
import { initials } from "@/lib/format";
import { ease, fadeIn, spring } from "@/lib/motion";
import { useMe } from "@/lib/queries";
import { PIN_COOKIE } from "@/lib/types";

import { LogoMark } from "./Logo";
import { LogoutButton } from "./LogoutButton";
import { RolePill } from "./RolePill";
import { ThemeToggle } from "./ThemeToggle";
import { Button } from "./ui/Button";
import { Skeleton } from "./ui/Skeleton";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

/** Nav entries for the current user (shared with BottomNav). */
export function useNav(): NavItem[] {
  const { data: me } = useMe();
  return [
    { label: "Overview", href: "/dashboard/overview", icon: LayoutDashboard },
    ...(me?.role === "admin"
      ? [{ label: "Users", href: "/dashboard/users", icon: Users }]
      : []),
  ];
}

const RAIL = 64;
const FULL = 232;
/** Hover intent: a pass-over doesn't open it, a brief exit doesn't close it. */
const OPEN_DELAY = 120;
const CLOSE_DELAY = 220;

/**
 * Desktop sidebar. Collapsed to a 64px icon rail by default; hovering (or
 * tabbing into) it expands it over the content. The panel button pins it
 * open, which pushes the content aside instead. Every icon sits on the
 * rail's centre line (x = 32px) so nothing shifts as it opens.
 */
export function Sidebar({ initialPinned = false }: { initialPinned?: boolean }) {
  const pathname = usePathname();
  const nav = useNav();
  const { data: me } = useMe();
  const reduce = useReducedMotion();

  const [pinned, setPinned] = useState(initialPinned);
  const [hovered, setHovered] = useState(false);
  const [focused, setFocused] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const open = pinned || hovered || focused;

  useEffect(() => () => clearTimeout(timer.current), []);

  function togglePin() {
    const next = !pinned;
    setPinned(next);
    // unpinning under the cursor should collapse now, not wait for a mouse move
    if (!next) {
      clearTimeout(timer.current);
      setHovered(false);
    }
    document.cookie = `${PIN_COOKIE}=${next ? 1 : 0}; path=/; max-age=31536000; samesite=lax`;
  }

  function hoverTo(next: boolean) {
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setHovered(next), next ? OPEN_DELAY : CLOSE_DELAY);
  }

  const width = { duration: reduce ? 0 : 0.24, ease };
  // labels fade in once the panel has room, and out before it narrows
  const label = cn(
    "whitespace-nowrap transition-opacity",
    open ? "opacity-100 delay-75 duration-200" : "opacity-0 duration-100",
  );

  return (
    // Reserves layout space: the rail, or the full width while pinned.
    <aside
      style={{ width: pinned ? FULL : RAIL }}
      className="sticky top-0 z-40 hidden h-screen shrink-0 transition-[width] duration-[240ms] ease-[cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none md:block"
    >
      <m.div
        initial={false}
        animate={{ width: open ? FULL : RAIL }}
        transition={width}
        onMouseEnter={() => hoverTo(true)}
        onMouseLeave={() => hoverTo(false)}
        // keyboard focus opens it; a mouse click (e.g. on the pin) must not hold it open
        onFocus={(e) => setFocused(e.target.matches(":focus-visible"))}
        onBlur={(e) => {
          if (!e.currentTarget.contains(e.relatedTarget as Node | null)) setFocused(false);
        }}
        className={cn(
          "absolute inset-y-0 left-0 flex flex-col overflow-hidden border-r border-border bg-surface transition-shadow duration-200",
          open && !pinned && "shadow-[8px_0_32px_rgb(0_0_0/0.18)]",
        )}
      >
        {/* Brand + pin toggle */}
        <div className="flex h-14 shrink-0 items-center justify-between pl-[21px] pr-3">
          <span className="flex items-center gap-2.5">
            <LogoMark />
            <span
              translate="no"
              className={cn("text-sm font-semibold tracking-tight text-fg", label)}
            >
              The Collector
            </span>
          </span>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={togglePin}
            aria-pressed={pinned}
            aria-label={pinned ? "Collapse sidebar" : "Keep sidebar open"}
            title={pinned ? "Collapse sidebar" : "Keep sidebar open"}
            className={label}
          >
            {pinned ? (
              <PanelLeftClose className="h-4 w-4" aria-hidden />
            ) : (
              <PanelLeftOpen className="h-4 w-4" aria-hidden />
            )}
          </Button>
        </div>

        <nav aria-label="Main" className="flex-1 space-y-0.5 px-4 pt-2">
          <AnimatePresence initial={false}>
            {nav.map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <m.div
                  key={item.href}
                  variants={fadeIn}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                >
                  <Link
                    href={item.href}
                    aria-current={active ? "page" : undefined}
                    title={open ? undefined : item.label}
                    className={cn(
                      "relative flex h-8 items-center gap-2.5 rounded-control px-2 text-sm font-medium transition-colors duration-150",
                      active
                        ? "text-fg"
                        : "text-fg-muted hover:bg-surface-2/60 hover:text-fg",
                    )}
                  >
                    {active && (
                      <m.span
                        layoutId="sidebar-active"
                        transition={spring}
                        className="absolute inset-0 rounded-control bg-surface-2"
                      />
                    )}
                    <Icon className="relative h-4 w-4 shrink-0" aria-hidden />
                    <span className={cn("relative", label)}>{item.label}</span>
                  </Link>
                </m.div>
              );
            })}
          </AnimatePresence>
        </nav>

        {/* Account: the avatar stays on the rail; name, role and actions reveal with the panel */}
        <div className="flex shrink-0 items-center gap-2.5 border-t border-border py-3 pl-4 pr-3">
          {me ? (
            <>
              <span
                aria-hidden
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface-2 text-xs font-medium text-fg-muted"
              >
                {initials(me.name)}
              </span>
              <div
                className={cn("flex min-w-0 flex-1 flex-col items-start gap-1", label)}
              >
                <p
                  className="w-full truncate text-sm font-medium leading-4 text-fg"
                  title={me.email}
                >
                  {me.name}
                </p>
                <RolePill
                  role={me.role}
                  className="!h-5 !gap-1 !px-2"
                />
              </div>
            </>
          ) : (
            <>
              <Skeleton className="h-8 w-8 shrink-0 !rounded-full" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-3.5 w-20" />
                <Skeleton className="h-3 w-12" />
              </div>
            </>
          )}
          <div className={cn("flex shrink-0 items-center", label)}>
            <ThemeToggle className="!h-8 !w-8" />
            <LogoutButton className="!h-8 !w-8" />
          </div>
        </div>
      </m.div>
    </aside>
  );
}
