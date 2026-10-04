import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const secret = process.env.CRON_SECRET;
  if (!secret || req.headers.get("authorization") !== `Bearer ${secret}`) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }
  const resp = await backendFetch("/health/db");
  return NextResponse.json({ ok: resp.ok }, { status: resp.ok ? 200 : 502 });
}
