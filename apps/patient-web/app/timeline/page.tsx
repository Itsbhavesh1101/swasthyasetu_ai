import { Timeline } from "../../components/timeline";
import { PageHeader } from "../../components/ui-primitives";

export default function TimelinePage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Longitudinal record"
        title="Medical timeline"
        description="Review your history entries and health journeys together in time order."
      />
      <Timeline />
    </div>
  );
}
