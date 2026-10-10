import { AppShell, EmptyState } from "@swasthyasetu/ui";

export default function ClinicianFoundationPage() {
  return (
    <AppShell title="SwasthyaSetu Clinician">
      <EmptyState
        description="This workspace contains the clinician application foundation. Clinical workflows will be added only in their governed phases."
        title="Foundation ready"
      />
    </AppShell>
  );
}
