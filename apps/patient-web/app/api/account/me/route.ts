import type { NextRequest } from "next/server";
import { readAccount } from "../../../../lib/account/server";
export async function GET(request: NextRequest) {
  return readAccount(request);
}
