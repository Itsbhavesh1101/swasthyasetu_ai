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
    console.error("Patient workspace route error", { digest: error.digest ?? "unavailable" });
  }, [error]);

  return (
    <AppShell title="SwasthyaSetu Patient">
      <ErrorState onRetry={reset} />
    </AppShell>
  );
}
