import type { Metadata } from "next";

import { ActionLink, PageHeader, Panel, StatusBanner } from "../components/ui-primitives";

export const metadata: Metadata = { title: "Home" };

export default function PatientHomePage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Private by design"
        title="Your health history, kept together"
        description="Create a private patient account to maintain your details, medical history, and documents. SwasthyaSetu does not provide a diagnosis."
      />

      <div className="hero-actions" aria-label="Patient actions">
        <ActionLink href="/register">Create account</ActionLink>
        <ActionLink href="/login" variant="secondary">
          Sign in
        </ActionLink>
        <ActionLink href="/urgent-help" variant="critical">
          Urgent help
        </ActionLink>
      </div>

      <StatusBanner title="You stay in control" tone="info">
        Authentication uses private HttpOnly session cookies. The browser does not store passwords,
        health information, or consent records in local storage.
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
