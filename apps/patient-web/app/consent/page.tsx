import type { Metadata } from "next";

import { ConsentJourney } from "../../components/consent-journey";
import { PageHeader } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Consent" };

export default function ConsentPage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        title="Review consent"
        description="Choose whether this temporary session may be used for general product use and future clinical-intake processing."
      />
      <ConsentJourney />
    </div>
  );
}
