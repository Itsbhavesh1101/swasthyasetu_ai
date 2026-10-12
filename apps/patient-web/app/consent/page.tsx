import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";

export const metadata: Metadata = { title: "Consent" };

export default function ConsentPage() {
  return (
    <RouteUnavailable
      availableIn="P6-B consent integration"
      description="Consent must be explained and recorded by the governed service before this step can be used."
      title="Consent"
    />
  );
}
