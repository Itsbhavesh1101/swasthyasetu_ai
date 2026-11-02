import type { Metadata } from "next";

import { MannSetuSyntheticPreview } from "../../components/mannsetu-synthetic-preview";
import { RouteUnavailable } from "../../components/route-unavailable";
import { loadEngineeringMannSetuPreview } from "../../lib/mannsetu-demo/server";

export const metadata: Metadata = { title: "MannSetu" };

export const dynamic = "force-dynamic";

export default async function MannSetuPage() {
  const outcome = await loadEngineeringMannSetuPreview();
  if (outcome.ok) return <MannSetuSyntheticPreview result={outcome.result} />;
  return (
    <RouteUnavailable
      availableIn="a future governed mental-health phase"
      description="Mental-health assessment, clinical policy, and verified resources are not configured in this build."
      title="MannSetu"
    />
  );
}
