import { Skeleton } from "./ui/Skeleton";

/** Shell-shaped placeholder shown while the route or the profile loads. */
export function PageSkeleton({ kpis = true }: { kpis?: boolean }) {
  return (
    <div role="status" aria-label="Loading">
      <div className="mb-6 space-y-2">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-4 w-64 max-w-full" />
      </div>
      {kpis && (
        <div className="mb-4 grid divide-y divide-border overflow-hidden rounded-panel border border-border bg-surface sm:grid-cols-2 sm:divide-x sm:divide-y-0">
          {[0, 1].map((i) => (
            <div key={i} className="space-y-2.5 px-5 py-4">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-8 w-36" />
              <Skeleton className="h-3 w-40" />
            </div>
          ))}
        </div>
      )}
      <div className="overflow-hidden rounded-panel border border-border bg-surface">
        <div className="border-b border-border px-4 py-3">
          <Skeleton className="h-7 w-48" />
        </div>
        {Array.from({ length: 5 }, (_, i) => (
          <div key={i} className="flex items-center gap-6 border-b border-border px-4 py-4 last:border-0">
            <Skeleton className="h-3.5 w-12" />
            <Skeleton className="h-3.5 w-24" />
            <Skeleton className="hidden h-3.5 w-16 sm:block" />
            <Skeleton className="ml-auto h-3.5 w-20" />
          </div>
        ))}
      </div>
    </div>
  );
}
