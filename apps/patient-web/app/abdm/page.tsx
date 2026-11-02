import type { Metadata } from "next";

import { ABDMSyntheticPreview } from "../../components/abdm-synthetic-preview";
import { RouteUnavailable } from "../../components/route-unavailable";
import { loadEngineeringABDMPreview } from "../../lib/abdm-demo/server";

export const metadata: Metadata = { title: "ABDM" };

export const dynamic = "force-dynamic";

export default async function ABDMPage() {
  const outcome = await loadEngineeringABDMPreview();
  if (outcome.ok) return <ABDMSyntheticPreview result={outcome.result} />;
  return (
    <RouteUnavailable
      availableIn="a future governed ABDM integration phase"
      description="Official protocols, ABHA identity, consent, sandbox access, and exchange transport are not configured in this build."
      title="ABDM integration"
    />
  );
}
