"use client";

import { useEffect } from "react";

import { ErrorState, PageHeader } from "../components/ui-primitives";

export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Patient page failed to render.");
  }, []);

  return (
    <div className="page-stack">
      <PageHeader title="We could not open this page" />
      <ErrorState onRetry={reset} />
    </div>
  );
}
