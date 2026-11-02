import type { NextRequest } from "next/server";

import { readEngineeringDemo } from "../../../../../../lib/demo/server";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ intakeId: string }> },
) {
  const { intakeId } = await params;
  return readEngineeringDemo(request, intakeId);
}
