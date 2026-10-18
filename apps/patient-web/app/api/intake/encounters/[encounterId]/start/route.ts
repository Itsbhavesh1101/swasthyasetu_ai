import { NextRequest } from "next/server";

import { startEncounterIntake } from "../../../../../../lib/intake/server";

export const dynamic = "force-dynamic";

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ encounterId: string }> },
) {
  const { encounterId } = await context.params;
  return startEncounterIntake(request, encounterId);
}
