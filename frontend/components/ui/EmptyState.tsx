import type { LucideIcon } from "lucide-react";

interface Props {
  icon: LucideIcon;
  title: string;
  /** One line that teaches what will appear here or what to do. */
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: Props) {
  return (
    <div className="flex flex-col items-center px-6 py-12 text-center">
      <span className="flex h-9 w-9 items-center justify-center rounded-panel border border-border text-fg-subtle">
        <Icon className="h-4 w-4" aria-hidden />
      </span>
      <p className="mt-3 text-sm font-medium text-fg">{title}</p>
      {description && (
        <p className="mt-1 max-w-xs text-sm text-fg-muted">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
