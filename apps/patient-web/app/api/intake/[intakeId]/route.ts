import { NextRequest } from "next/server";

import { readIntake } from "../../../../lib/intake/server";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ intakeId: string }> },
) {
  const { intakeId } = await context.params;
  return readIntake(request, intakeId);
}
