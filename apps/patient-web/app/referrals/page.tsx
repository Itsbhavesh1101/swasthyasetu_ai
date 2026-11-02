import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";
import { ReferralDiscoveryPreview } from "../../components/referral-discovery-preview";
import { loadEngineeringReferralDiscovery } from "../../lib/referral-demo/server";

export const metadata: Metadata = { title: "Referrals" };

export const dynamic = "force-dynamic";

export default async function ReferralsPage() {
  const outcome = await loadEngineeringReferralDiscovery();
  if (outcome.ok) return <ReferralDiscoveryPreview result={outcome.result} />;
  return (
    <RouteUnavailable
      availableIn="the governed referral phase"
      description="Verified providers and referral pathways are not configured in this build."
      title="Referrals"
    />
  );
}
