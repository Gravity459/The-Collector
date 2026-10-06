"use client";

import { Check } from "lucide-react";

import { useApproveCollection } from "@/lib/queries";
import type { Collection } from "@/lib/types";

import { Button } from "./ui/Button";

export function ApproveButton({ collection }: { collection: Collection }) {
  const approve = useApproveCollection();
  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={() => approve.mutate(collection)}
      loading={approve.isPending}
    >
      <Check className="h-3.5 w-3.5" aria-hidden />
      Approve
    </Button>
  );
}
