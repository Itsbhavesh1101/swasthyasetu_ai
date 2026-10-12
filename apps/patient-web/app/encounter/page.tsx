import type { Metadata } from "next";

import { OnboardingReadiness } from "../../components/onboarding-readiness";
import { PageHeader } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Health journey" };

export default function EncounterPage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        title="Health journey"
        description="Check whether the private onboarding steps are ready. No encounter or clinical intake is created here."
      />
      <OnboardingReadiness />
    </div>
  );
}
