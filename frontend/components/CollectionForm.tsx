"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { CURRENCY } from "@/lib/format";
import { useCreateCollection } from "@/lib/queries";

import { Button } from "./ui/Button";
import { Field } from "./ui/Field";
import { Input } from "./ui/Input";
import { Panel } from "./ui/Panel";

const schema = z.object({
  house_number: z.coerce
    .number({ invalid_type_error: "Enter the house number" })
    .int("Use a whole number")
    .positive("Enter the house number"),
  amount: z.coerce
    .number({ invalid_type_error: "Enter the amount" })
    .int("Use a whole amount")
    .positive("Enter the amount"),
});

type FormValues = z.infer<typeof schema>;

/**
 * Inline entry form: logging a collection is the collector's main job, so it
 * is always on screen. After each submit the fields clear and focus returns
 * to the house number, ready for the next door.
 */
export function CollectionForm() {
  const create = useCreateCollection();
  const {
    register,
    handleSubmit,
    reset,
    setFocus,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  function onSubmit(values: FormValues) {
    create.mutate(values, {
      onSuccess: () => {
        reset();
        setFocus("house_number");
      },
    });
  }

  return (
    <Panel aria-labelledby="new-collection-title" className="p-4 sm:p-5">
      <h2 id="new-collection-title" className="text-sm font-medium text-fg">
        New collection
      </h2>
      <form
        onSubmit={handleSubmit(onSubmit)}
        noValidate
        className="mt-3 grid grid-cols-2 gap-3 sm:flex sm:items-start"
      >
        <Field label="House number" error={errors.house_number?.message} className="sm:w-40">
          <Input
            type="number"
            inputMode="numeric"
            min={1}
            prefix="S-"
            placeholder="14"
            touch
            autoComplete="off"
            {...register("house_number")}
          />
        </Field>
        <Field label="Amount" error={errors.amount?.message} className="sm:w-44">
          <Input
            type="number"
            inputMode="numeric"
            min={1}
            prefix={CURRENCY}
            placeholder="5000"
            touch
            autoComplete="off"
            {...register("amount")}
          />
        </Field>
        <Button
          type="submit"
          variant="primary"
          loading={create.isPending}
          className="col-span-2 h-11 sm:mt-[22px] sm:h-9"
        >
          Submit collection
        </Button>
      </form>
    </Panel>
  );
}
