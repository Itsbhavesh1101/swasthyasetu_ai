import { NextRequest, NextResponse } from "next/server";

import {
  SESSION_ID_COOKIE,
  SESSION_TOKEN_COOKIE,
  sessionCookieOptions,
} from "../onboarding/server";
import { validateMutationOrigin } from "../security/request-origin";

const TIMEOUT_MS = 15_000;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const OUTCOMES = new Set([
  "ANSWERED",
  "OUT_OF_SCOPE",
  "CONSENT_REQUIRED",
  "UNAVAILABLE",
  "REJECTED",
]);
type RecordValue = Record<string, unknown>;

const record = (value: unknown): value is RecordValue =>
  typeof value === "object" && value !== null && !Array.isArray(value);

function json(body: unknown, status = 200) {
  const response = NextResponse.json(body, { status });
  response.headers.set("Cache-Control", "no-store");
  return response;
}

const failure = (status: number, message: string) =>
  json({ error: { code: "GUIDANCE_REQUEST_FAILED", message } }, status);

function origin() {
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

function credentials(request: NextRequest) {
  const sessionId = request.cookies.get(SESSION_ID_COOKIE)?.value;
  const token = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  return sessionId && UUID.test(sessionId) && token ? { sessionId, token } : undefined;
}

function clear(request: NextRequest, response: NextResponse) {
  const options = sessionCookieOptions(request.nextUrl.hostname || undefined);
  response.cookies.set(SESSION_ID_COOKIE, "", { ...options, maxAge: 0 });
  response.cookies.set(SESSION_TOKEN_COOKIE, "", { ...options, maxAge: 0 });
  return response;
}

async function backend(request: NextRequest, path: string, init: RequestInit) {
  const current = credentials(request);
  if (!current) return { anonymous: true } as const;
  const base = origin();
  if (!base) return undefined;
  try {
    const response = await fetch(`${base}${path}`, {
      ...init,
      cache: "no-store",
      headers: { Authorization: `Bearer ${current.token}`, ...init.headers },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    return { response } as const;
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

function authFailure(request: NextRequest, status: number) {
  return status === 401 ? clear(request, json({ state: "ANONYMOUS" }, 401)) : undefined;
}

export async function readGuidanceConsent(request: NextRequest) {
  const result = await backend(request, "/api/v1/guidance/consent", { method: "GET" });
  if (result && "anonymous" in result) return json({ state: "ANONYMOUS" }, 401);
  if (!result) return failure(503, "Guidance consent is unavailable.");
  const invalid = authFailure(request, result.response.status);
  if (invalid) return invalid;
  const body = await value(result.response);
  if (
    !result.response.ok ||
    !record(body) ||
    typeof body.active !== "boolean" ||
    body.notice_version !== "external-ai-v1" ||
    !Array.isArray(body.scope) ||
    body.scope.length !== 1 ||
    body.scope[0] !== "ayurvedic_guidance"
  )
    return failure(502, "Guidance consent could not be loaded.");
  return json({
    state: "AUTHENTICATED",
    active: body.active,
    noticeVersion: "external-ai-v1",
    scope: ["ayurvedic_guidance"],
  });
}

async function mutateConsent(request: NextRequest, method: "POST" | "DELETE") {
  const rejected = validateMutationOrigin(request);
  if (rejected)
    return json({ error: { code: rejected.code, message: rejected.message } }, rejected.status);
  const result = await backend(request, "/api/v1/guidance/consent", { method });
  if (result && "anonymous" in result) return json({ state: "ANONYMOUS" }, 401);
  if (!result) return failure(503, "Guidance consent is unavailable.");
  const invalid = authFailure(request, result.response.status);
  if (invalid) return invalid;
  return result.response.ok
    ? json({ state: "AUTHENTICATED", active: method === "POST" })
    : failure(502, "Guidance consent could not be updated.");
}

export const grantGuidanceConsent = (request: NextRequest) => mutateConsent(request, "POST");
export const revokeGuidanceConsent = (request: NextRequest) => mutateConsent(request, "DELETE");

const submissionLocks = new Map<string, Promise<void>>();

async function serialized<T>(key: string, task: () => Promise<T>): Promise<T> {
  const previous = submissionLocks.get(key) ?? Promise.resolve();
  let release!: () => void;
  const gate = new Promise<void>((resolve) => (release = resolve));
  const queued = previous.then(() => gate);
  submissionLocks.set(key, queued);
  await previous;
  try {
    return await task();
  } finally {
    release();
    if (submissionLocks.get(key) === queued) submissionLocks.delete(key);
  }
}

export async function requestGuidance(request: NextRequest) {
  const rejected = validateMutationOrigin(request);
  if (rejected)
    return json({ error: { code: rejected.code, message: rejected.message } }, rejected.status);
  const current = credentials(request);
  if (!current) return json({ state: "ANONYMOUS" }, 401);
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return failure(400, "Enter a valid wellness question.");
  }
  if (
    !record(body) ||
    typeof body.question !== "string" ||
    !body.question.trim() ||
    body.question.length > 1_000
  )
    return failure(400, "Enter a valid wellness question.");
  return serialized(current.sessionId, async () => {
    const result = await backend(request, "/api/v1/guidance/ayurveda", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: body.question }),
    });
    if (!result || "anonymous" in result) return failure(503, "Guidance is unavailable.");
    const invalid = authFailure(request, result.response.status);
    if (invalid) return invalid;
    const data = await value(result.response);
    if (
      !result.response.ok ||
      !record(data) ||
      typeof data.outcome !== "string" ||
      !OUTCOMES.has(data.outcome)
    )
      return failure(502, "Guidance is unavailable.");
    if (data.outcome !== "ANSWERED") return json({ outcome: data.outcome, citations: [] });
    if (
      typeof data.answer !== "string" ||
      !data.answer ||
      !Array.isArray(data.citations) ||
      !data.citations.every(
        (citation) =>
          record(citation) &&
          typeof citation.title === "string" &&
          typeof citation.url === "string" &&
          citation.url.startsWith("https://"),
      ) ||
      typeof data.retrieved_at !== "string" ||
      Number.isNaN(Date.parse(data.retrieved_at))
    )
      return failure(502, "Guidance is unavailable.");
    return json({
      outcome: "ANSWERED",
      answer: data.answer,
      citations: data.citations,
      retrievedAt: data.retrieved_at,
    });
  });
}
