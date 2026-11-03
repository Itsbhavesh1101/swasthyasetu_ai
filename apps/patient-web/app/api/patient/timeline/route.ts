import type { NextRequest } from "next/server";
import { readTimeline } from "../../../../lib/timeline/server";
export const GET = (request: NextRequest) => readTimeline(request);
