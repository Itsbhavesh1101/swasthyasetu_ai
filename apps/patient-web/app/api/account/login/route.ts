import type { NextRequest } from "next/server";
import { loginAccount } from "../../../../lib/account/server";
export async function POST(request: NextRequest) {
  return loginAccount(request);
}
