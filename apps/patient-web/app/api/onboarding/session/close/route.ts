import type { NextRequest } from "next/server";

import { closeSession } from "../../../../../lib/onboarding/server";

export async function POST(request: NextRequest) {
  return closeSession(request);
}
