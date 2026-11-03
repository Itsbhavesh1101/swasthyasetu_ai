import { NextRequest, NextResponse } from "next/server";

import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../onboarding/server";
import type { TimelineItem } from "./contracts";

const TIMEOUT_MS = 5_000;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
type RecordValue = Record<string, unknown>;
const record = (value: unknown): value is RecordValue =>
  typeof value === "object" && value !== null && !Array.isArray(value);

function json(body: unknown, status = 200) {
  const response = NextResponse.json(body, { status });
  response.headers.set("Cache-Control", "no-store");
  return response;
}

function backendOrigin() {
  const configured = process.env.SWASTHYASETU_BACKEND_URL?.trim();
  if (!configured) return undefined;
  try {
    const url = new URL(configured);
    const loopback = ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
    return (url.protocol === "https:" || (url.protocol === "http:" && loopback)) &&
      url.pathname === "/" &&
      !url.search &&
      !url.hash &&
      !url.username &&
      !url.password
      ? url.origin
      : undefined;
  } catch {
    return undefined;
  }
}

function token(request: NextRequest) {
  const sessionId = request.cookies.get(SESSION_ID_COOKIE)?.value;
  const bearer = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  return sessionId && UUID.test(sessionId) && bearer ? bearer : undefined;
}

async function backend(path: string, bearer: string) {
  const base = backendOrigin();
  if (!base) return undefined;
  try {
    return await fetch(`${base}${path}`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${bearer}` },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    return undefined;
  }
}

async function value(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

function item(value: unknown): TimelineItem | undefined {
  if (
    !record(value) ||
    typeof value.entry_id !== "string" ||
    !UUID.test(value.entry_id) ||
    !["ENCOUNTER", "CLINICAL_FACT"].includes(String(value.entry_type)) ||
    typeof value.occurred_at !== "string" ||
    Number.isNaN(Date.parse(value.occurred_at))
  )
    return undefined;
  if (value.entry_type === "CLINICAL_FACT") {
    if (typeof value.fact_type !== "string" || typeof value.canonical_label !== "string")
      return undefined;
    return {
      entryId: value.entry_id,
      entryType: "CLINICAL_FACT",
      occurredAt: value.occurred_at,
      category: value.fact_type.replaceAll("_", " "),
      label: value.canonical_label,
      detail: String(value.verification_state).replaceAll("_", " "),
    };
  }
  if (typeof value.encounter_type !== "string" || typeof value.status !== "string")
    return undefined;
  return {
    entryId: value.entry_id,
    entryType: "ENCOUNTER",
    occurredAt: value.occurred_at,
    category: "Health journey",
    label: value.encounter_type.replaceAll("_", " "),
    detail: value.status.replaceAll("_", " "),
  };
}

export async function readTimeline(request: NextRequest) {
  const bearer = token(request);
  if (!bearer) return json({ state: "ANONYMOUS" }, 401);
  const account = await backend("/api/v1/accounts/me", bearer);
  if (!account) return json({ error: { code: "TIMELINE_UNAVAILABLE" } }, 503);
  const accountBody = await value(account);
  if (account.status === 401) return json({ state: "ANONYMOUS" }, 401);
  if (
    !account.ok ||
    !record(accountBody) ||
    typeof accountBody.patient_id !== "string" ||
    !UUID.test(accountBody.patient_id)
  )
    return json({ error: { code: "TIMELINE_UNAVAILABLE" } }, 502);
  const cursor = request.nextUrl.searchParams.get("cursor");
  if (cursor !== null && (!cursor || cursor.length > 1024))
    return json({ error: { code: "INVALID_CURSOR" } }, 400);
  const query = new URLSearchParams({ limit: "25" });
  if (cursor) query.set("cursor", cursor);
  const response = await backend(
    `/api/v1/patients/${accountBody.patient_id}/timeline?${query.toString()}`,
    bearer,
  );
  if (!response) return json({ error: { code: "TIMELINE_UNAVAILABLE" } }, 503);
  const body = await value(response);
  if (!response.ok || !record(body) || !Array.isArray(body.items))
    return json({ error: { code: "TIMELINE_UNAVAILABLE" } }, response.status === 401 ? 401 : 502);
  const items = body.items.map(item);
  if (
    items.some((entry) => entry === undefined) ||
    (body.next_cursor !== null && typeof body.next_cursor !== "string")
  )
    return json({ error: { code: "TIMELINE_UNAVAILABLE" } }, 502);
  return json({
    state: "AUTHENTICATED",
    items,
    ...(body.next_cursor ? { nextCursor: body.next_cursor } : {}),
  });
}
