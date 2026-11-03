import type { Metadata } from "next";

import { AccountIntakeReadiness } from "../../components/account-intake-readiness";
import { PageHeader } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Health journey" };

export default function EncounterPage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        title="Health journey"
        description="Use your patient account to start or resume a structured intake draft."
      />
      <AccountIntakeReadiness />
    </div>
  );
}
