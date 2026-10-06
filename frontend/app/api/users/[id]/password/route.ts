import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const body = await req.json();
  const resp = await backendFetch(`/api/v1/users/${id}/password`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
  if (resp.status === 204) {
    return new NextResponse(null, { status: 204 });
  }
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}
