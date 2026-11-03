import type { NextRequest } from "next/server";
import { registerAccount } from "../../../../lib/account/server";
export async function POST(request: NextRequest) {
  return registerAccount(request);
}
