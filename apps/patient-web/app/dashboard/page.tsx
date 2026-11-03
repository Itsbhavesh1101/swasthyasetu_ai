import { ActionLink, PageHeader, Panel } from "../../components/ui-primitives";
export default function DashboardPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Patient dashboard"
        title="Your health record"
        description="Build your profile, record your medical history, and keep documents together."
      />
      <section className="feature-grid">
        <Panel>
          <h2>Personal details</h2>
          <p>Add the details that help describe you.</p>
          <ActionLink href="/profile">Open profile</ActionLink>
        </Panel>
        <Panel>
          <h2>Medical history</h2>
          <p>Record conditions, medicines, allergies, procedures, and observations.</p>
          <ActionLink href="/history">Open history</ActionLink>
        </Panel>
        <Panel>
          <h2>Documents</h2>
          <p>Keep your reports and prescriptions in your private vault.</p>
          <ActionLink href="/documents">Open documents</ActionLink>
        </Panel>
      </section>
    </div>
  );
}
