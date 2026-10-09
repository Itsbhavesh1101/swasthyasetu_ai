import { AppShell, EmptyState } from "@swasthyasetu/ui";

export default function AdminFoundationPage() {
  return (
    <AppShell title="SwasthyaSetu Admin">
      <EmptyState
        description="This workspace contains the administration application foundation. Governance features will be added only in their governed phases."
        title="Foundation ready"
      />
    </AppShell>
  );
}
