import type { NextRequest } from "next/server";
import { requestGuidance } from "../../../lib/guidance/server";
export const POST = (request: NextRequest) => requestGuidance(request);
