import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export async function GET() {
  const resp = await backendFetch("/api/v1/collections/total");
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}
