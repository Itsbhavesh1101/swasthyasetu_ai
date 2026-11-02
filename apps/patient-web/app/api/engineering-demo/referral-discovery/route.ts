import { readEngineeringReferralDiscovery } from "../../../../lib/referral-demo/server";

export const dynamic = "force-dynamic";

export async function GET() {
  return readEngineeringReferralDiscovery();
}
