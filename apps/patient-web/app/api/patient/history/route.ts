import type { NextRequest } from "next/server";

import { addHistory, readHistory } from "../../../../lib/history/server";

export async function GET(request: NextRequest) {
  return readHistory(request);
}

export async function POST(request: NextRequest) {
  return addHistory(request);
}
