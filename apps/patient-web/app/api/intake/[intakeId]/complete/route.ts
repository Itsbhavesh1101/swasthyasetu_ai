import { NextRequest } from "next/server";

import { completeIntake } from "../../../../../lib/intake/server";

export const dynamic = "force-dynamic";

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ intakeId: string }> },
) {
  const { intakeId } = await context.params;
  return completeIntake(request, intakeId);
}
