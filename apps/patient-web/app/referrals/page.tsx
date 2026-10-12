import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";

export const metadata: Metadata = { title: "Referrals" };

export default function ReferralsPage() {
  return (
    <RouteUnavailable
      availableIn="the governed referral phase"
      description="Verified providers and referral pathways are not configured in this build."
      title="Referrals"
    />
  );
}
