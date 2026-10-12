import { LoadingState, PageHeader } from "../components/ui-primitives";

export default function Loading() {
  return (
    <div className="page-stack">
      <PageHeader title="Preparing this page" description="Please wait a moment." />
      <LoadingState label="Loading patient page" />
    </div>
  );
}
