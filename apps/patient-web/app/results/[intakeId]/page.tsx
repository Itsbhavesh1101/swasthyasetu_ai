import type { Metadata } from "next";

import { EngineeringResult } from "../../../components/demo/engineering-result";

export const metadata: Metadata = { title: "Synthetic result preview" };

export default async function EngineeringResultPage({
  params,
}: {
  params: Promise<{ intakeId: string }>;
}) {
  const { intakeId } = await params;
  return <EngineeringResult intakeId={intakeId} />;
}
