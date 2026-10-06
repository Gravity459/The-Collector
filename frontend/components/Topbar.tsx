"use client";

import { Logo } from "./Logo";
import { LogoutButton } from "./LogoutButton";
import { ThemeToggle } from "./ThemeToggle";

/** Phone-only top bar. Navigation lives in BottomNav. */
export function Topbar() {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-border bg-bg/85 px-4 backdrop-blur-md md:hidden">
      <Logo />
      <div className="flex items-center gap-1">
        <ThemeToggle />
        <LogoutButton />
      </div>
    </header>
  );
}
