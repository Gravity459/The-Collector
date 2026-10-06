"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { KeyRound, Plus, Trash2, Users } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { formatDate, initials, relativeTime } from "@/lib/format";
import { useCreateUser, useDeleteUser, useMe, useUsers } from "@/lib/queries";
import type { User } from "@/lib/types";

import { ConfirmModal } from "./ConfirmModal";
import { PageHeader } from "./PageHeader";
import { Pagination } from "./Pagination";
import { PasswordModal } from "./PasswordModal";
import { RolePill } from "./RolePill";
import { Button } from "./ui/Button";
import { type Column, DataTable } from "./ui/DataTable";
import { Dialog } from "./ui/Dialog";
import { EmptyState } from "./ui/EmptyState";
import { Field } from "./ui/Field";
import { Input, Select } from "./ui/Input";
import { Panel, PanelHeader } from "./ui/Panel";

const schema = z.object({
  name: z.string().trim().min(1, "Enter a name").max(255),
  email: z.string().trim().email("Enter a valid email, like name@example.com"),
  password: z.string().min(8, "Use at least 8 characters").max(128),
  role: z.enum(["collector", "user", "admin"]),
});

type FormValues = z.infer<typeof schema>;

function CreateUserDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const create = useCreateUser();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { role: "collector" },
  });

  function close() {
    reset();
    create.reset();
    onClose();
  }

  function onSubmit(values: FormValues) {
    create.mutate(values, { onSuccess: close });
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => !next && close()}
      title="New user"
      description="They can sign in right away with this email and password."
      busy={create.isPending}
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <Field label="Name" error={errors.name?.message}>
          <Input autoComplete="off" autoFocus {...register("name")} />
        </Field>
        <Field label="Email" error={errors.email?.message}>
          <Input
            type="email"
            autoComplete="off"
            spellCheck={false}
            placeholder="name@example.com"
            {...register("email")}
          />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Password" error={errors.password?.message}>
            <Input
              type="password"
              autoComplete="new-password"
              {...register("password")}
            />
          </Field>
          <Field label="Role" error={errors.role?.message}>
            <Select {...register("role")}>
              <option value="collector">Collector</option>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </Select>
          </Field>
        </div>
        <div className="flex flex-col-reverse gap-2 pt-2 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={close} disabled={create.isPending}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={create.isPending}>
            Create user
          </Button>
        </div>
      </form>
    </Dialog>
  );
}

export function UsersView() {
  const [page, setPage] = useState(1);
  const [creating, setCreating] = useState(false);
  const [passwordUser, setPasswordUser] = useState<User | null>(null);
  const [removeUser, setRemoveUser] = useState<User | null>(null);

  const { data: me } = useMe();
  const { data, isLoading, isPlaceholderData } = useUsers(page);
  const remove = useDeleteUser();

  function confirmRemove() {
    if (!removeUser) return;
    const { id, email } = removeUser;
    remove.mutate(id, {
      onSuccess: () => {
        setRemoveUser(null);
        toast.success(`${email} removed`);
      },
    });
  }

  const columns: Column<User>[] = [
    {
      key: "user",
      header: "User",
      mobile: "primary",
      cell: (u) => (
        <span className="flex min-w-0 items-center gap-3">
          <span
            aria-hidden
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface-2 text-xs font-medium text-fg-muted"
          >
            {initials(u.name)}
          </span>
          <span className="min-w-0">
            <span className="block truncate font-medium text-fg">
              {u.name}
              {u.id === me?.id && (
                <span className="ml-1.5 font-normal text-fg-subtle">(you)</span>
              )}
            </span>
            <span className="block truncate text-xs text-fg-muted">{u.email}</span>
          </span>
        </span>
      ),
    },
    {
      key: "role",
      header: "Role",
      align: "center",
      mobile: "end",
      cell: (u) => <RolePill role={u.role} />,
    },
    {
      key: "joined",
      header: "Added",
      align: "center",
      cell: (u) => (
        <time
          dateTime={u.created_at}
          title={formatDate(u.created_at)}
          className="whitespace-nowrap text-fg-muted"
        >
          <span className="sm:hidden">Added </span>
          {relativeTime(u.created_at)}
        </time>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      align: "center",
      mobile: "actions",
      className: "w-[1%] whitespace-nowrap",
      cell: (u) => (
        <span className="inline-flex items-center justify-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPasswordUser(u)}
            aria-label={`Change password for ${u.email}`}
            title="Change password"
          >
            <KeyRound className="h-3.5 w-3.5" aria-hidden />
            {/* icon-only until there is room, so the table never scrolls sideways */}
            <span className="hidden lg:inline">Change password</span>
          </Button>
          {u.id !== me?.id ? (
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={`Remove ${u.email}`}
              title="Remove user"
              className="hover:!bg-danger-bg hover:!text-danger"
              onClick={() => setRemoveUser(u)}
            >
              <Trash2 className="h-4 w-4" aria-hidden />
            </Button>
          ) : (
            // keeps "Change password" aligned with the rows that can be removed
            <span aria-hidden className="inline-block h-7 w-7" />
          )}
        </span>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Users"
        description="Create accounts, reset passwords and remove access."
      >
        <Button variant="primary" onClick={() => setCreating(true)}>
          <Plus className="h-4 w-4" aria-hidden />
          New user
        </Button>
      </PageHeader>

      <Panel>
        <PanelHeader title="All users" count={data?.total} />
        <DataTable
          columns={columns}
          rows={data?.items ?? []}
          getRowId={(u) => u.id}
          isLoading={isLoading}
          isFetching={isPlaceholderData}
          pageKey={`users-${page}`}
          caption="All users"
          empty={
            <EmptyState
              icon={Users}
              title="No users yet"
              description="Add collectors, residents and admins so they can sign in."
            />
          }
        />
        <Pagination
          page={data?.page ?? page}
          totalPages={data?.total_pages ?? 0}
          total={data?.total ?? 0}
          onChange={setPage}
        />
      </Panel>

      <CreateUserDialog open={creating} onClose={() => setCreating(false)} />

      <PasswordModal user={passwordUser} onClose={() => setPasswordUser(null)} />

      <ConfirmModal
        open={removeUser !== null}
        title={`Remove ${removeUser?.name ?? "user"}?`}
        message={`${removeUser?.email ?? "This user"} will lose access immediately. Collections they submitted are kept. This can't be undone.`}
        confirmLabel="Remove user"
        loading={remove.isPending}
        onConfirm={confirmRemove}
        onCancel={() => setRemoveUser(null)}
      />
    </div>
  );
}
