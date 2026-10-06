interface Props {
  title: string;
  description?: string;
  /** Toolbar on the right (filters, primary action). */
  children?: React.ReactNode;
}

export function PageHeader({ title, description, children }: Props) {
  return (
    <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div className="min-w-0">
        <h1 className="text-balance text-lg font-semibold tracking-tight text-fg">{title}</h1>
        {description && <p className="mt-1 text-sm text-fg-muted">{description}</p>}
      </div>
      {children && (
        <div className="flex flex-wrap items-center gap-2">{children}</div>
      )}
    </div>
  );
}
