import type { NextRequest } from "next/server";

import { readPatientProfile, updatePatientProfile } from "../../../../lib/patient/server";

export async function GET(request: NextRequest) {
  return readPatientProfile(request);
}

export async function PATCH(request: NextRequest) {
  return updatePatientProfile(request);
}
