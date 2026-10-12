import type { Metadata } from "next";

import { ActionLink, PageHeader, Panel, StatusBanner } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Urgent help" };

export default function UrgentHelpPage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="Urgent help"
        title="Get help now if you feel unsafe"
        description="This page is a visible route to urgent support. It does not assess symptoms or choose care for you."
      />
      <StatusBanner title="Verified resources are not configured" tone="critical">
        <p>
          This build does not contain verified helpline numbers, providers, or local crisis
          contacts. We will not guess or show unverified contact details.
        </p>
      </StatusBanner>
      <Panel>
        <h2>If there may be immediate danger</h2>
        <p>
          Seek urgent help from local emergency services or a trusted person nearby. Do not rely on
          this website for an emergency response.
        </p>
      </Panel>
      <ActionLink href="/" variant="secondary">
        Return home
      </ActionLink>
    </div>
  );
}
