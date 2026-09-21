"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useCreateCollection } from "@/lib/queries";

const schema = z.object({
  house_number: z.coerce.number().int().positive("Enter a house number"),
  amount: z.coerce.number().int().positive("Enter an amount"),
});

type FormValues = z.infer<typeof schema>;

export function CollectionForm() {
  const create = useCreateCollection();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  function onSubmit(values: FormValues) {
    create.mutate(values, { onSuccess: () => reset() });
  }

  const input =
    "w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 outline-none transition placeholder:text-zinc-400 focus:border-accent focus:ring-2 focus:ring-accent/30 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100";

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm sm:p-5 dark:border-zinc-800 dark:bg-zinc-900"
    >
      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
        New collection
      </h2>
      <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="w-full sm:w-40">
          <label className="mb-1 block text-xs font-medium text-zinc-500 dark:text-zinc-400">
            House number
          </label>
          <input type="number" min={1} {...register("house_number")} className={input} />
          {errors.house_number && (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">
              {errors.house_number.message}
            </p>
          )}
        </div>
        <div className="w-full sm:w-40">
          <label className="mb-1 block text-xs font-medium text-zinc-500 dark:text-zinc-400">
            Amount
          </label>
          <input type="number" min={1} {...register("amount")} className={input} />
          {errors.amount && (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">
              {errors.amount.message}
            </p>
          )}
        </div>
        <button
          type="submit"
          disabled={create.isPending}
          className="w-full rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition hover:bg-accent-hover disabled:opacity-60 sm:w-auto"
        >
          {create.isPending ? "Submitting…" : "Submit collection"}
        </button>
      </div>
      {create.isError && (
        <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-500/10 dark:text-red-400">
          {axios.isAxiosError(create.error) &&
          create.error.response?.data?.detail
            ? create.error.response.data.detail
            : "Could not submit. Please try again."}
        </p>
      )}
    </form>
  );
}
