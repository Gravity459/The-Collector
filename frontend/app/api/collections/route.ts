import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export async function GET(req: Request) {
  const qs = new URL(req.url).search; // includes leading "?" or ""
  const resp = await backendFetch(`/api/v1/collections${qs}`);
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}

export async function POST(req: Request) {
  const body = await req.json();
  const resp = await backendFetch("/api/v1/collections", {
    method: "POST",
    body: JSON.stringify(body),
  });
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}
