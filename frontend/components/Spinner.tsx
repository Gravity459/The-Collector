interface Props {
  size?: "sm" | "md" | "lg";
  label?: string;
  /** Center within a tall area (e.g. initial page load). */
  center?: boolean;
}

const SIZES: Record<NonNullable<Props["size"]>, string> = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-10 w-10 border-[3px]",
};

export function Spinner({ size = "md", label, center }: Props) {
  const ring = (
    <div className="flex flex-col items-center gap-3">
      <div
        role="status"
        aria-label={label ?? "Loading"}
        className={`${SIZES[size]} animate-spin rounded-full border-zinc-200 border-t-accent dark:border-zinc-700 dark:border-t-accent-soft`}
      />
      {label && (
        <span className="text-sm text-zinc-500 dark:text-zinc-400">{label}</span>
      )}
    </div>
  );

  if (center) {
    return (
      <div className="flex min-h-[60vh] w-full items-center justify-center">
        {ring}
      </div>
    );
  }
  return ring;
}
