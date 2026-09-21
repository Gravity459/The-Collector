import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export async function PATCH(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const resp = await backendFetch(`/api/v1/collections/${id}/approve`, {
    method: "PATCH",
  });
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}
