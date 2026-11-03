import { DashboardOverview } from "../../components/dashboard-overview";
import { PageHeader } from "../../components/ui-primitives";
export default function DashboardPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Patient dashboard"
        title="Your health record"
        description="Build your profile, record your medical history, and keep documents together."
      />
      <DashboardOverview />
    </div>
  );
}
