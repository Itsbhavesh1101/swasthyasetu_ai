import type { Metadata } from "next";

import { OfflineActions } from "../../components/offline-actions";
import { PageHeader, StatusBanner } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Offline" };

export default function OfflinePage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="Connection unavailable"
        title="You appear to be offline"
        description="Session and consent status cannot be confirmed without a connection."
      />
      <StatusBanner title="Clinical workflows are unavailable offline" tone="critical">
        <p>
          Nothing will be submitted or queued while you are offline. Reconnect before continuing any
          private-session or consent action.
        </p>
      </StatusBanner>
      <p>
        Urgent-help information here is not a substitute for emergency services. This site cannot
        confirm local services while offline.
      </p>
      <OfflineActions />
    </div>
  );
}
