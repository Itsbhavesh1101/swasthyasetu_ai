import type { Metadata } from "next";

import { IntakeJourney } from "../../../../components/intake/intake-journey";

export const metadata: Metadata = { title: "Review intake draft" };

export default async function IntakeReviewPage({
  params,
}: {
  params: Promise<{ intakeId: string }>;
}) {
  const { intakeId } = await params;
  return <IntakeJourney intakeId={intakeId} review />;
}
