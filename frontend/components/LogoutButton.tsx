"use client";

import { useQueryClient } from "@tanstack/react-query";
import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "./ui/Button";

export function LogoutButton({ className }: { className?: string }) {
  const router = useRouter();
  const qc = useQueryClient();
  const [pending, setPending] = useState(false);

  async function logout() {
    setPending(true);
    await fetch("/api/auth/logout", { method: "POST" });
    qc.clear();
    router.replace("/login");
    router.refresh();
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={logout}
      loading={pending}
      aria-label="Sign out"
      title="Sign out"
      className={className}
    >
      <LogOut className="h-4 w-4" aria-hidden />
    </Button>
  );
}
