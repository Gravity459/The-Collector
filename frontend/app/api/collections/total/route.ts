import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export async function GET(req: Request) {
  const qs = new URL(req.url).search; // includes leading "?" or ""
  const resp = await backendFetch(`/api/v1/collections/total${qs}`);
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}
