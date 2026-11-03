import type { NextRequest } from "next/server";
import {
  grantGuidanceConsent,
  readGuidanceConsent,
  revokeGuidanceConsent,
} from "../../../../lib/guidance/server";
export const GET = (request: NextRequest) => readGuidanceConsent(request);
export const POST = (request: NextRequest) => grantGuidanceConsent(request);
export const DELETE = (request: NextRequest) => revokeGuidanceConsent(request);
