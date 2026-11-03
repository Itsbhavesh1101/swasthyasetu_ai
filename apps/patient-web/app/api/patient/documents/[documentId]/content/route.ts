import type { NextRequest } from "next/server";
import { downloadDocument } from "../../../../../../lib/documents/server";
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ documentId: string }> },
) {
  return downloadDocument(request, (await params).documentId);
}
