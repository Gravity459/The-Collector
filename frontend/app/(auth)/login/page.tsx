"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";

const schema = z.object({
  email: z.string().email("Enter a valid email, like name@example.com"),
  password: z.string().min(1, "Enter your password"),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const [redirecting, setRedirecting] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      toast.error(
        typeof data.detail === "string"
          ? data.detail
          : "Couldn't sign in. Check your email and password.",
      );
      return;
    }
    // keep the button busy until the dashboard replaces this page
    setRedirecting(true);
    router.replace("/dashboard/overview");
    router.refresh();
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center px-4 py-10">
      <div className="absolute right-4 top-4">
        <ThemeToggle />
      </div>

      <div className="w-full max-w-[360px]">
        <Logo />
        <h1 className="mt-8 text-balance text-lg font-semibold tracking-tight text-fg">
          Sign in to The Collector
        </h1>
        <p className="mt-1 text-sm text-fg-muted">
          Use the email and password your admin gave you.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} noValidate className="mt-6 space-y-4">
          <Field label="Email" error={errors.email?.message}>
            <Input
              type="email"
              autoComplete="email"
              spellCheck={false}
              touch
              placeholder="name@example.com"
              {...register("email")}
            />
          </Field>
          <Field label="Password" error={errors.password?.message}>
            <Input
              type="password"
              autoComplete="current-password"
              touch
              {...register("password")}
            />
          </Field>
          <Button
            type="submit"
            variant="primary"
            loading={isSubmitting || redirecting}
            className="h-11 w-full sm:h-9"
          >
            Sign in
          </Button>
        </form>
      </div>
    </main>
  );
}
