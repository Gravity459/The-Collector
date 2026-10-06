"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useUpdateUserPassword } from "@/lib/queries";
import type { User } from "@/lib/types";

import { Button } from "./ui/Button";
import { Dialog } from "./ui/Dialog";
import { Field } from "./ui/Field";
import { Input } from "./ui/Input";

const schema = z.object({
  password: z.string().min(8, "Use at least 8 characters").max(128),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  /** The user whose password is being changed; null closes the dialog. */
  user: User | null;
  onClose: () => void;
}

export function PasswordModal({ user, onClose }: Props) {
  const update = useUpdateUserPassword();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  // fresh form and mutation state each time the dialog opens
  useEffect(() => {
    if (user) {
      reset();
      update.reset();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  function onSubmit(values: FormValues) {
    if (!user) return;
    update.mutate({ id: user.id, password: values.password }, { onSuccess: onClose });
  }

  return (
    <Dialog
      open={user !== null}
      onOpenChange={(next) => !next && onClose()}
      title="Change password"
      description={user ? `Set a new password for ${user.email}.` : undefined}
      busy={update.isPending}
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Field label="New password" error={errors.password?.message}>
          <Input
            type="password"
            autoComplete="new-password"
            autoFocus
            {...register("password")}
          />
        </Field>
        <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={onClose} disabled={update.isPending}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={update.isPending}>
            Save password
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
