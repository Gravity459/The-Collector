"use client";

import { Trash2 } from "lucide-react";
import { useState } from "react";

import { houseLabel } from "@/lib/format";
import { useDeleteCollection } from "@/lib/queries";
import type { Collection } from "@/lib/types";

import { ConfirmModal } from "./ConfirmModal";
import { Button } from "./ui/Button";

export function RemoveButton({ collection }: { collection: Collection }) {
  const [open, setOpen] = useState(false);
  const remove = useDeleteCollection();
  const house = houseLabel(collection.house_number);

  function confirm() {
    // optimistic: the row leaves the table as soon as the dialog closes
    setOpen(false);
    remove.mutate({ collection, successMessage: `Payment for ${house} removed` });
  }

  return (
    <>
      <Button
        variant="ghost"
        size="icon-sm"
        aria-label={`Remove payment for ${house}`}
        title="Remove"
        className="hover:!bg-danger-bg hover:!text-danger"
        onClick={() => setOpen(true)}
      >
        <Trash2 className="h-4 w-4" aria-hidden />
      </Button>

      <ConfirmModal
        open={open}
        title={`Remove ${house}'s payment?`}
        message={`The approved payment for ${house} will be deleted and taken out of the month's total. This can't be undone.`}
        confirmLabel="Remove payment"
        onConfirm={confirm}
        onCancel={() => setOpen(false)}
      />
    </>
  );
}
