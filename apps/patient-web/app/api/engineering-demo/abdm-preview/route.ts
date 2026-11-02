import { readEngineeringABDMPreview } from "../../../../lib/abdm-demo/server";

export const dynamic = "force-dynamic";

export async function GET() {
  return readEngineeringABDMPreview();
}
