import { HistoryList } from "../../components/history-list";
import { PageHeader } from "../../components/ui-primitives";

export default function HistoryPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Your health record"
        title="Medical history"
        description="Record conditions, medicines, allergies, procedures, observations, and investigations in one place."
      />
      <HistoryList />
    </div>
  );
}
