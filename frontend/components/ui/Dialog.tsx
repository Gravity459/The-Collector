"use client";

import { X } from "lucide-react";
import { AnimatePresence, useDragControls } from "motion/react";
import * as m from "motion/react-m";
import { useEffect, useId, useRef, useSyncExternalStore } from "react";
import { createPortal } from "react-dom";

import { cn } from "@/lib/cn";
import { dialog as dialogVariants, fadeIn, sheet } from "@/lib/motion";
import { PHONE_QUERY, useMediaQuery } from "@/lib/useMediaQuery";

import { Button } from "./Button";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: React.ReactNode;
  children?: React.ReactNode;
  /** Footer actions, right-aligned on desktop, full-width on phones. */
  footer?: React.ReactNode;
  /** Block closing (Esc, backdrop, drag) while a request is in flight. */
  busy?: boolean;
  className?: string;
}

/**
 * Accessible modal built on the native <dialog> element: showModal() makes the
 * rest of the page inert, contains focus, closes on Esc and restores focus to
 * the trigger. Centred on desktop; a bottom sheet with drag-to-dismiss on phones.
 */
const noopSubscribe = () => () => {};

export function Dialog(props: Props) {
  // Portal to <body>: a dialog opened from a table row must not inherit the
  // row's opacity/transform animations or the cell's text alignment.
  // portal only after mount: the server and the first client render both output nothing
  const mounted = useSyncExternalStore(
    noopSubscribe,
    () => true,
    () => false,
  );
  if (!mounted) return null;
  return createPortal(
    <AnimatePresence>{props.open && <DialogInner {...props} />}</AnimatePresence>,
    document.body,
  );
}

function DialogInner({
  onOpenChange,
  title,
  description,
  children,
  footer,
  busy = false,
  className,
}: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  const phone = useMediaQuery(PHONE_QUERY, { sync: true });
  const drag = useDragControls();
  const titleId = useId();
  const descId = useId();
  const busyRef = useRef(busy);
  busyRef.current = busy;

  function requestClose() {
    if (!busyRef.current) onOpenChange(false);
  }

  // Open as a modal on mount; close (restoring focus) after the exit animation unmounts us.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (!el.open) el.showModal();
    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = overflow;
      if (el.open) el.close();
    };
  }, []);

  return (
    <dialog
      ref={ref}
      aria-labelledby={titleId}
      aria-describedby={description ? descId : undefined}
      onCancel={(e) => {
        // Esc: animate out through React state instead of closing instantly
        e.preventDefault();
        requestClose();
      }}
      className="fixed inset-0 m-0 h-full max-h-none w-full max-w-none overflow-hidden bg-transparent p-0 backdrop:bg-transparent"
    >
      <m.div
        variants={fadeIn}
        initial="initial"
        animate="animate"
        exit="exit"
        onClick={requestClose}
        className="absolute inset-0 bg-black/50 dark:bg-black/70"
        aria-hidden
      />
      <div
        className={cn(
          "pointer-events-none absolute inset-0 flex",
          phone ? "items-end" : "items-center justify-center p-4",
        )}
      >
        <m.div
          variants={phone ? sheet : dialogVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          drag={phone && !busy ? "y" : false}
          dragControls={drag}
          dragListener={false}
          dragConstraints={{ top: 0, bottom: 0 }}
          dragElastic={{ top: 0, bottom: 0.6 }}
          onDragEnd={(_, info) => {
            if (info.offset.y > 120 || info.velocity.y > 500) requestClose();
          }}
          className={cn(
            // reset what the dialog would inherit from where it is rendered (e.g. a table cell)
            "pointer-events-auto relative w-full whitespace-normal border border-border bg-surface text-left text-base font-normal text-fg shadow-[0_16px_48px_rgb(0_0_0/0.28)]",
            phone
              ? "max-h-[90dvh] overflow-y-auto overscroll-contain rounded-t-dialog px-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] pt-2"
              : "max-w-md rounded-dialog p-6",
            className,
          )}
        >
          {phone && (
            <div
              onPointerDown={(e) => drag.start(e)}
              className="-mx-5 mb-2 flex cursor-grab touch-none justify-center py-2 active:cursor-grabbing"
              aria-hidden
            >
              <span className="h-1 w-10 rounded-full bg-border-strong" />
            </div>
          )}
          <div className="pr-8">
            <h2 id={titleId} className="text-md font-medium tracking-tight text-fg">
              {title}
            </h2>
            {description && (
              <p id={descId} className="mt-1.5 text-sm text-fg-muted">
                {description}
              </p>
            )}
          </div>
          {children && <div className="mt-5">{children}</div>}
          {footer && (
            <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              {footer}
            </div>
          )}
          {!phone && (
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Close"
              disabled={busy}
              onClick={requestClose}
              className="!absolute right-4 top-4"
            >
              <X className="h-4 w-4" aria-hidden />
            </Button>
          )}
        </m.div>
      </div>
    </dialog>
  );
}
