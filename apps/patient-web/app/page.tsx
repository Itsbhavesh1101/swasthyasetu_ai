import { ActionLink, PageHeader, Panel, StatusBanner } from "../components/ui-primitives";

export default function PatientHomePage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Private by design"
        title="Your health journey, one step at a time"
        description="SwasthyaSetu offers a clear place to begin sharing health information when you are ready. It does not provide a diagnosis."
      />

      <div className="hero-actions" aria-label="Patient actions">
        <ActionLink href="/start">Get started</ActionLink>
        <ActionLink href="/urgent-help" variant="critical">
          Urgent help
        </ActionLink>
      </div>

      <StatusBanner title="You stay in control" tone="info">
        Nothing is saved in your browser by this shell. Session and consent steps will be connected
        in the next governed phase.
      </StatusBanner>

      <section aria-labelledby="what-to-expect-title" className="feature-grid">
        <Panel>
          <p className="card-kicker">01</p>
          <h2 id="what-to-expect-title">Start when you are ready</h2>
          <p>
            The guided start will explain what information is needed before asking you to share
            anything.
          </p>
        </Panel>
        <Panel>
          <p className="card-kicker">02</p>
          <h2>Clear, respectful steps</h2>
          <p>
            Future journeys will show what is available, what is not, and when more information is
            needed.
          </p>
        </Panel>
        <Panel>
          <p className="card-kicker">03</p>
          <h2>Help stays within reach</h2>
          <p>
            The urgent-help entry point remains visible throughout the patient experience without
            making unverified service claims.
          </p>
        </Panel>
      </section>
    </div>
  );
}
