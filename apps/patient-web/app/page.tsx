import { AppShell, EmptyState } from "@swasthyasetu/ui";

export default function PatientFoundationPage() {
  return (
    <AppShell title="SwasthyaSetu Patient">
      <EmptyState
        description="This workspace contains the patient application foundation. Product workflows will be added only in their governed phases."
        title="Foundation ready"
      />
    </AppShell>
  );
}
