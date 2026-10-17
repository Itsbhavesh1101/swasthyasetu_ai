import type { Metadata } from "next";

import { IntakeJourney } from "../../../components/intake/intake-journey";

export const metadata: Metadata = { title: "Structured intake" };

export default async function IntakePage({ params }: { params: Promise<{ intakeId: string }> }) {
  const { intakeId } = await params;
  return <IntakeJourney intakeId={intakeId} />;
}
