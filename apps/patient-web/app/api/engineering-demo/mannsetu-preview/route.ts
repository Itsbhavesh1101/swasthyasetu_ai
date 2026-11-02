import { readEngineeringMannSetuPreview } from "../../../../lib/mannsetu-demo/server";

export const dynamic = "force-dynamic";

export async function GET() {
  return readEngineeringMannSetuPreview();
}
