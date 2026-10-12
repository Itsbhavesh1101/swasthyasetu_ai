import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";

export const metadata: Metadata = { title: "Documents" };

export default function DocumentsPage() {
  return (
    <RouteUnavailable
      availableIn="the governed document phase"
      description="Document upload and review are not enabled in this build."
      title="Documents"
    />
  );
}
