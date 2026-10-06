"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LazyMotion, MotionConfig } from "motion/react";
import { useState } from "react";
import { Toaster } from "sonner";

import { PHONE_QUERY, useMediaQuery } from "@/lib/useMediaQuery";

const motionFeatures = () => import("@/lib/motion-features").then((mod) => mod.default);

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 30_000, refetchOnWindowFocus: false },
        },
      }),
  );
  // toasts sit bottom-right on desktop and top-centre on phones
  const position = useMediaQuery(PHONE_QUERY) ? "top-center" : "bottom-right";

  return (
    <QueryClientProvider client={client}>
      <LazyMotion features={motionFeatures} strict>
        <MotionConfig reducedMotion="user">{children}</MotionConfig>
      </LazyMotion>
      <Toaster
        position={position}
        closeButton
        toastOptions={{
          // follow the app's class-based theme instead of sonner's own
          classNames: {
            toast:
              "!rounded-panel !border !border-border !bg-surface !text-fg !text-sm !shadow-[0_8px_24px_rgb(0_0_0/0.18)] !font-sans",
            description: "!text-fg-muted",
            closeButton: "!border-border !bg-surface !text-fg-muted",
            success: "[&_[data-icon]]:!text-success",
            error: "[&_[data-icon]]:!text-danger",
          },
        }}
      />
    </QueryClientProvider>
  );
}
