import type { NextRequest } from "next/server";

import { createSession, readSession } from "../../../../lib/onboarding/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  return readSession(request);
}

export async function POST(request: NextRequest) {
  return createSession(request);
}
