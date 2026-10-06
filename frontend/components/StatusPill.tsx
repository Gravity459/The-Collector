import { Pill } from "./ui/Pill";

/** Green = Approved, grey = Pending Approval. */
export function StatusPill({ approved }: { approved: boolean }) {
  return approved ? (
    <Pill tone="text-success" bg="bg-success-bg">
      Approved
    </Pill>
  ) : (
    <Pill tone="text-pending" bg="bg-pending-bg">
      Pending approval
    </Pill>
  );
}
