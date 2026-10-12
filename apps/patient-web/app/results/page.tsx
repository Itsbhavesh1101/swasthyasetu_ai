import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";

export const metadata: Metadata = { title: "Results" };

export default function ResultsPage() {
  return (
    <RouteUnavailable
      availableIn="a future results workflow"
      description="There are no connected results to show. This page will not fabricate health information."
      title="Results"
    />
  );
}
