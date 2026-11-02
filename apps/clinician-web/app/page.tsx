import { AppShell } from "@swasthyasetu/ui";

import { EngineeringDocumentReview } from "../components/engineering-document-review";
import { EngineeringSummaryReview } from "../components/engineering-summary-review";
import { loadEngineeringDocumentResult } from "../lib/document-demo/server";
import { loadEngineeringSummaryResult } from "../lib/summary-demo/server";

export const dynamic = "force-dynamic";

export default async function ClinicianFoundationPage() {
  const [documentOutcome, summaryOutcome] = await Promise.all([
    loadEngineeringDocumentResult(),
    loadEngineeringSummaryResult(),
  ]);
  return (
    <AppShell title="SwasthyaSetu Clinician">
      <header className="page-header">
        <p className="eyebrow">College demonstration</p>
        <h2>Clinician engineering workspace</h2>
        <p>
          Only offline synthetic contract evidence is shown. Live clinical workflows remain off.
        </p>
      </header>
      <EngineeringDocumentReview result={documentOutcome.ok ? documentOutcome.result : null} />
      <EngineeringSummaryReview result={summaryOutcome.ok ? summaryOutcome.result : null} />
    </AppShell>
  );
}
