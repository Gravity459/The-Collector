import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export const dynamic = "force-dynamic";
// the sweep writes to Google one job at a time; give it room
export const maxDuration = 60;

/** Daily Vercel Cron: retry sheet writes that are pending or failed. */
export async function GET(req: Request) {
  const secret = process.env.CRON_SECRET;
  if (!secret || req.headers.get("authorization") !== `Bearer ${secret}`) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }
  const resp = await backendFetch("/api/v1/sheet-sync/sweep", {
    method: "POST",
    headers: { "X-Cron-Secret": secret },
  });
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}
