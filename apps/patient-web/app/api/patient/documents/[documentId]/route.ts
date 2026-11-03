import type { NextRequest } from "next/server";
import { deleteDocument } from "../../../../../lib/documents/server";
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ documentId: string }> },
) {
  return deleteDocument(request, (await params).documentId);
}
