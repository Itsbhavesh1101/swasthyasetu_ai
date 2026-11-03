import type { NextRequest } from "next/server";
import { logoutAccount } from "../../../../lib/account/server";
export async function POST(request: NextRequest) {
  return logoutAccount(request);
}
