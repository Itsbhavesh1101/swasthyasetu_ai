import type { NextRequest } from "next/server";

import { revokeConsent } from "../../../../../lib/onboarding/server";

export async function POST(request: NextRequest) {
  return revokeConsent(request);
}
