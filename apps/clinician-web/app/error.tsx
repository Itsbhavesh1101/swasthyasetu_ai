"use client";

import { AppShell, ErrorState } from "@swasthyasetu/ui";
import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Clinician workspace route error", { digest: error.digest ?? "unavailable" });
  }, [error]);

  return (
    <AppShell title="SwasthyaSetu Clinician">
      <ErrorState onRetry={reset} />
    </AppShell>
  );
}
