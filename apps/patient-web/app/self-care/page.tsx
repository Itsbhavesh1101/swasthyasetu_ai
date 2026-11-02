import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";
import { SelfCareSyntheticPreview } from "../../components/self-care-synthetic-preview";
import { loadEngineeringSelfCarePreview } from "../../lib/self-care-demo/server";

export const metadata: Metadata = { title: "Self-care" };

export const dynamic = "force-dynamic";

export default async function SelfCarePage() {
  const outcome = await loadEngineeringSelfCarePreview();
  if (outcome.ok) return <SelfCareSyntheticPreview result={outcome.result} />;
  return (
    <RouteUnavailable
      availableIn="a future governed self-care phase"
      description="Approved self-care knowledge, clinical eligibility, and guidance are not configured in this build."
      title="Self-care"
    />
  );
}
