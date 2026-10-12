import type { NextRequest } from "next/server";

import { grantConsent, readConsent } from "../../../../lib/onboarding/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  return readConsent(request);
}

export async function POST(request: NextRequest) {
  return grantConsent(request);
}
