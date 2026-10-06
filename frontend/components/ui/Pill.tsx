import { cn } from "@/lib/cn";

interface Props {
  /** Text colour class for label + dot, e.g. "text-success". */
  tone: string;
  /** Background class, e.g. "bg-success-bg". */
  bg: string;
  children: React.ReactNode;
  className?: string;
}

/** Base pill: tinted background, same-hue text and a dot (never colour alone). */
export function Pill({ tone, bg, children, className }: Props) {
  return (
    <span
      className={cn(
        "inline-flex h-[22px] items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 text-xs font-medium",
        tone,
        bg,
        className,
      )}
    >
      <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-current" />
      {children}
    </span>
  );
}
