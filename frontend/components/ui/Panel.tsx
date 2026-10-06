import { cn } from "@/lib/cn";

interface Props extends React.HTMLAttributes<HTMLElement> {
  as?: "section" | "div";
}

/** Bordered surface. Panels are the only container; never nest them. */
export function Panel({ children, className, as: Tag = "section", ...rest }: Props) {
  return (
    <Tag
      className={cn(
        "overflow-hidden rounded-panel border border-border bg-surface",
        className,
      )}
      {...rest}
    >
      {children}
    </Tag>
  );
}

/** Panel header row: title (+ optional count) on the left, actions on the right. */
export function PanelHeader({
  title,
  count,
  children,
  className,
}: {
  title?: React.ReactNode;
  count?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3 border-b border-border px-4 py-3 sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
    >
      {title != null && (
        <div className="flex min-h-7 items-center gap-2">
          <h2 className="text-sm font-medium text-fg">{title}</h2>
          {count != null && (
            <span className="rounded-full bg-surface-2 px-2 py-0.5 text-xs tabular-nums text-fg-muted">
              {count}
            </span>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
