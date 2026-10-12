import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";

export const metadata: Metadata = { title: "Health journey" };

export default function EncounterPage() {
  return (
    <RouteUnavailable
      availableIn="a future governed workflow"
      description="The health-information journey is not enabled, so this page cannot collect or display information."
      title="Health journey"
    />
  );
}
