import { NextResponse } from "next/server";

import { backendFetch } from "@/lib/server";

export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const resp = await backendFetch(`/api/v1/collections/${id}`, {
    method: "DELETE",
  });
  if (resp.status === 204) {
    return new NextResponse(null, { status: 204 });
  }
  const data = await resp.json().catch(() => ({}));
  return NextResponse.json(data, { status: resp.status });
}
