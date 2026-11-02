import { readEngineeringSummaryResult } from "../../../../lib/summary-demo/server";

export const dynamic = "force-dynamic";

export async function GET() {
  return readEngineeringSummaryResult();
}
