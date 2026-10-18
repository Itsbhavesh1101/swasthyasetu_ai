import type { Metadata } from "next";

import { OnboardingReadiness } from "../../components/onboarding-readiness";
import { PageHeader } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Health journey" };

export default function EncounterPage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        title="Health journey"
        description="Check your private session and consent, then start a structured intake draft."
      />
      <OnboardingReadiness />
    </div>
  );
}
