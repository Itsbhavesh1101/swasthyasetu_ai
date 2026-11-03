import type { NextRequest } from "next/server";

import { supersedeHistory } from "../../../../../../lib/history/server";

export async function POST(request: NextRequest, context: { params: Promise<{ factId: string }> }) {
  return supersedeHistory(request, (await context.params).factId);
}
