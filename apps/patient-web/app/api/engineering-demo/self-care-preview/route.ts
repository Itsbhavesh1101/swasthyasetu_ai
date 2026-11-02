import { readEngineeringSelfCarePreview } from "../../../../lib/self-care-demo/server";

export const dynamic = "force-dynamic";

export async function GET() {
  return readEngineeringSelfCarePreview();
}
