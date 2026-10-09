import { AppShell, LoadingState } from "@swasthyasetu/ui";

export default function Loading() {
  return (
    <AppShell title="SwasthyaSetu Patient">
      <LoadingState label="Loading patient workspace" />
    </AppShell>
  );
}
