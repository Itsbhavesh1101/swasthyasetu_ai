import { AppShell, LoadingState } from "@swasthyasetu/ui";

export default function Loading() {
  return (
    <AppShell title="SwasthyaSetu Admin">
      <LoadingState label="Loading administration workspace" />
    </AppShell>
  );
}
