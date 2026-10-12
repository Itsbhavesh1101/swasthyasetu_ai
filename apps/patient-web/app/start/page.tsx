import type { Metadata } from "next";

import { ActionLink, PageHeader, Panel, StatusBanner } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Start" };

export default function StartPage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="Private onboarding"
        title="Begin privately, at your pace"
        description="No name is required. We will start a temporary pseudonymous session after you choose a language."
      />
      <Panel>
        <h2>What happens next</h2>
        <p>Choose a session language, then review consent before any future clinical intake.</p>
      </Panel>
      <StatusBanner title="Urgent help stays available" tone="critical">
        <p>
          SwasthyaSetu is not an emergency service. Use the urgent-help page if you may be unsafe.
        </p>
      </StatusBanner>
      <div className="hero-actions">
        <ActionLink href="/language">Continue</ActionLink>
        <ActionLink href="/urgent-help" variant="critical">
          Urgent help
        </ActionLink>
      </div>
    </div>
  );
}
