import type { Metadata } from "next";

import { GuidanceForm } from "../../components/guidance-form";
import { PageHeader } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Ayurvedic home-care guidance" };

export default function GuidancePage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Grounded wellness education"
        title="Ayurvedic and home-care guidance"
        description="Ask a low-risk general wellness question and see source-backed educational information."
      />
      <GuidanceForm />
    </div>
  );
}
