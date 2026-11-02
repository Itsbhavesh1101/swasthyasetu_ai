import { AppShell } from "@swasthyasetu/ui";

import { EngineeringDocumentReview } from "../components/engineering-document-review";
import { loadEngineeringDocumentResult } from "../lib/document-demo/server";

export const dynamic = "force-dynamic";

export default async function ClinicianFoundationPage() {
  const outcome = await loadEngineeringDocumentResult();
  return (
    <AppShell title="SwasthyaSetu Clinician">
      <header className="page-header">
        <p className="eyebrow">College demonstration</p>
        <h2>Clinician engineering workspace</h2>
        <p>
          Only offline synthetic contract evidence is shown. Live clinical workflows remain off.
        </p>
      </header>
      <EngineeringDocumentReview result={outcome.ok ? outcome.result : null} />
    </AppShell>
  );
}
