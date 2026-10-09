import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export async function POST(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const resp = await backendFetch(`/api/v1/sheet-sync/jobs/${id}/retry`, {
    method: "POST",
  });
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}
