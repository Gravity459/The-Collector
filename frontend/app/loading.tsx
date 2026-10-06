import { Logo } from "@/components/Logo";
import { Skeleton } from "@/components/ui/Skeleton";

export default function Loading() {
  return (
    <div role="status" aria-label="Loading" className="flex min-h-screen w-full items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Logo />
        <Skeleton className="h-1 w-24 !rounded-full" />
      </div>
    </div>
  );
}
