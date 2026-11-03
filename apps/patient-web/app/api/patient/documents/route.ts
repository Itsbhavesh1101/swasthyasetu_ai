import type { NextRequest } from "next/server";
import { listDocuments, uploadDocument } from "../../../../lib/documents/server";
export const GET = (request: NextRequest) => listDocuments(request);
export const POST = (request: NextRequest) => uploadDocument(request);
