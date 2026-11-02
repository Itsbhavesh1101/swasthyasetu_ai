import type { Metadata } from "next";

import { FHIRSyntheticPreview } from "../../components/fhir-synthetic-preview";
import { RouteUnavailable } from "../../components/route-unavailable";
import { loadEngineeringFHIRPreview } from "../../lib/fhir-demo/server";

export const metadata: Metadata = { title: "FHIR" };

export const dynamic = "force-dynamic";

export default async function FHIRPage() {
  const outcome = await loadEngineeringFHIRPreview();
  if (outcome.ok) return <FHIRSyntheticPreview result={outcome.result} />;
  return (
    <RouteUnavailable
      availableIn="a future governed interoperability phase"
      description="Profile packages, patient mappings, exchange transport, and ABDM integration are not configured in this build."
      title="FHIR interoperability"
    />
  );
}
