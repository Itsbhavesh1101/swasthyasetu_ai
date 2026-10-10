import { AppShell, LoadingState } from "@swasthyasetu/ui";

export default function Loading() {
  return (
    <AppShell title="SwasthyaSetu Clinician">
      <LoadingState label="Loading clinician workspace" />
    </AppShell>
  );
}
