"use client";

import { Moon, Sun } from "lucide-react";
import { AnimatePresence } from "motion/react";
import * as m from "motion/react-m";
import { useEffect, useState } from "react";

import { fade } from "@/lib/motion";

import { Button } from "./ui/Button";

export function ThemeToggle({ className }: { className?: string }) {
  const [dark, setDark] = useState<boolean | null>(null);

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  function toggle() {
    const next = !document.documentElement.classList.contains("dark");
    const apply = () => {
      document.documentElement.classList.toggle("dark", next);
      setDark(next);
    };
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {
      /* ignore */
    }
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // crossfade the whole page where supported; plain swap otherwise
    if (document.startViewTransition && !reduce) document.startViewTransition(apply);
    else apply();
  }

  // Sun in dark mode (switch to light) / Moon in light mode
  const Icon = dark ? Sun : Moon;

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggle}
      aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
      title={dark ? "Light theme" : "Dark theme"}
      className={className}
    >
      <AnimatePresence mode="wait" initial={false}>
        {dark !== null && (
          <m.span
            key={dark ? "sun" : "moon"}
            initial={{ opacity: 0, rotate: -45 }}
            animate={{ opacity: 1, rotate: 0, transition: fade }}
            exit={{ opacity: 0, rotate: 45, transition: fade }}
            className="flex"
          >
            <Icon className="h-4 w-4" aria-hidden />
          </m.span>
        )}
      </AnimatePresence>
    </Button>
  );
}
