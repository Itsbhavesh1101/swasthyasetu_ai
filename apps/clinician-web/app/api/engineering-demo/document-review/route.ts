import { readEngineeringDocumentResult } from "../../../../lib/document-demo/server";

export const dynamic = "force-dynamic";

export async function GET() {
  return readEngineeringDocumentResult();
}
