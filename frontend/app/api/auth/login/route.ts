import { NextResponse } from "next/server";

import { BACKEND_URL } from "@/lib/server";
import { COOKIE_NAME } from "@/lib/types";

export async function POST(req: Request) {
  const body = await req.json();

  const resp = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({}));
    return NextResponse.json(
      { detail: detail.detail ?? "Login failed" },
      { status: resp.status },
    );
  }

  const data = await resp.json();
  const res = NextResponse.json({ ok: true });
  res.cookies.set(COOKIE_NAME, data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24, // 1 day
  });
  return res;
}
