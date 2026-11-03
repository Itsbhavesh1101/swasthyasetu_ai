import type { Metadata } from "next";

import { AccountForm } from "../components/account-form";
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

      <div className="account-entry-grid">
        <section aria-labelledby="sign-in-title">
          <h2 id="sign-in-title">Sign in</h2>
          <p>Continue to your private health dashboard.</p>
          <AccountForm mode="login" />
        </section>
        <section aria-labelledby="register-title">
          <h2 id="register-title">Create an account</h2>
          <p>Start with your email and a secure password. Your profile comes next.</p>
          <AccountForm mode="register" />
        </section>
      </div>
      <div className="hero-actions" aria-label="Help actions">
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
