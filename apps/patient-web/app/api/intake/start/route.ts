import { NextRequest } from "next/server";

import { createEncounterAndIntake } from "../../../../lib/intake/server";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  return createEncounterAndIntake(request);
}
