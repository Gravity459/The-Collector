"use client";

import { X } from "lucide-react";
import { useState } from "react";

import { houseLabel } from "@/lib/format";
import { useDeleteCollection } from "@/lib/queries";
import type { Collection } from "@/lib/types";

import { ConfirmModal } from "./ConfirmModal";
import { Button } from "./ui/Button";

export function RejectButton({ collection }: { collection: Collection }) {
  const [open, setOpen] = useState(false);
  const reject = useDeleteCollection();
  const house = houseLabel(collection.house_number);

  function confirm() {
    // optimistic: the row leaves the table as soon as the dialog closes
    setOpen(false);
    reject.mutate({ collection, successMessage: `Collection for ${house} rejected` });
  }

  return (
    <>
      <Button
        variant="ghost"
        size="icon-sm"
        aria-label={`Reject collection for ${house}`}
        title="Reject"
        className="hover:!bg-danger-bg hover:!text-danger"
        onClick={() => setOpen(true)}
      >
        <X className="h-4 w-4" aria-hidden />
      </Button>

      <ConfirmModal
        open={open}
        title={`Reject ${house}?`}
        message={`The pending collection for ${house} will be deleted. This can't be undone.`}
        confirmLabel="Reject collection"
        onConfirm={confirm}
        onCancel={() => setOpen(false)}
      />
    </>
  );
}
