export function StatusPill({ approved }: { approved: boolean }) {
  return approved ? (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700 dark:bg-green-500/15 dark:text-green-400">
      <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
      Approved
    </span>
  ) : (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-zinc-200 px-3 py-1 text-xs font-medium text-zinc-600 dark:bg-zinc-700/60 dark:text-zinc-300">
      <span className="h-1.5 w-1.5 rounded-full bg-zinc-400 dark:bg-zinc-500" />
      Pending Approval
    </span>
  );
}
