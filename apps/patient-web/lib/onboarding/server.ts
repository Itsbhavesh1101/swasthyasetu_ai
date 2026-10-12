import { NextRequest, NextResponse } from "next/server";

export const SESSION_ID_COOKIE = "swasthyasetu_session_id";
export const SESSION_TOKEN_COOKIE = "swasthyasetu_session_token";

const PURPOSE = "GENERAL_PRODUCT_USE";
const SCOPE = ["clinical_intake"] as const;
const NOTICE_VERSION = "privacy-v1";
const REQUEST_TIMEOUT_MS = 5_000;
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SESSION_STATUSES = new Set(["ACTIVE", "CLOSED", "EXPIRED", "REVOKED"]);
const CONSENT_STATUSES = new Set(["GRANTED", "REVOKED", "EXPIRED", "SUPERSEDED"]);

type JsonRecord = Record<string, unknown>;
type BackendResult = {
  ok: boolean;
  status: number;
  data: unknown;
  errorCode?: string;
};

type SessionCredentials = { sessionId: string; token: string };

type SessionView = {
  session_id: string;
  session_type: "PSEUDONYMOUS";
  status: string;
  language_preference?: string | null;
  expires_at: string;
};

type ConsentView = {
  consent_id: string;
  subject_type: "SESSION";
  subject_id: string;
  purpose: typeof PURPOSE;
  scope: string[];
  notice_version: string;
  status: string;
  granted_at: string;
};

const SAFE_BACKEND_ERROR_CODES = new Set([
  "AUTHENTICATION_REQUIRED",
  "AUTHORIZATION_DENIED",
  "DEPENDENCY_TIMEOUT",
  "DEPENDENCY_UNAVAILABLE",
  "INVALID_STATE_TRANSITION",
  "PROCESSING_FAILED",
  "RESOURCE_CONFLICT",
  "RESOURCE_NOT_FOUND",
  "SESSION_EXPIRED",
  "VALIDATION_ERROR",
]);

function isLoopbackHostname(hostname: string): boolean {
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1";
}

function requestHostname(request: NextRequest): string | undefined {
  const host = request.headers.get("host");
  if (!host) return request.nextUrl.hostname || undefined;
  try {
    return new URL(`${request.nextUrl.protocol}//${host}`).hostname;
  } catch {
    return undefined;
  }
}

export function sessionCookieOptions(hostname?: string) {
  return {
    httpOnly: true,
    sameSite: "strict" as const,
    path: "/",
    secure:
      process.env.NODE_ENV === "production" ||
      hostname === undefined ||
      !isLoopbackHostname(hostname),
  };
}

function noStore(response: NextResponse): NextResponse {
  response.headers.set("Cache-Control", "no-store");
  return response;
}

function json(body: unknown, status = 200): NextResponse {
  return noStore(NextResponse.json(body, { status }));
}

function safeError(code: string, message: string, status: number): NextResponse {
  return json({ error: { code, message } }, status);
}

function clearSessionCookies(request: NextRequest, response: NextResponse): NextResponse {
  const options = sessionCookieOptions(requestHostname(request));
  response.cookies.set(SESSION_ID_COOKIE, "", { ...options, maxAge: 0 });
  response.cookies.set(SESSION_TOKEN_COOKIE, "", { ...options, maxAge: 0 });
  return response;
}

function rejectCrossOrigin(request: NextRequest): NextResponse | undefined {
  const origin = request.headers.get("origin");
  const host = request.headers.get("host");
  const requestOrigin = host ? `${request.nextUrl.protocol}//${host}` : request.nextUrl.origin;
  if (origin && origin !== requestOrigin) {
    return safeError("ORIGIN_REJECTED", "This request origin is not allowed.", 403);
  }
  return undefined;
}

function configuredBackendUrl(): string | undefined {
  const configured = process.env.SWASTHYASETU_BACKEND_URL?.trim();
  if (!configured) return undefined;
  try {
    const parsed = new URL(configured);
    if (
      !["http:", "https:"].includes(parsed.protocol) ||
      parsed.username ||
      parsed.password ||
      parsed.pathname !== "/" ||
      parsed.search ||
      parsed.hash ||
      (parsed.protocol === "http:" && !isLoopbackHostname(parsed.hostname))
    ) {
      return undefined;
    }
    return parsed.origin;
  } catch {
    return undefined;
  }
}

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function canonicalErrorCode(data: unknown): string | undefined {
  if (!isRecord(data) || !isRecord(data.error) || typeof data.error.code !== "string") {
    return undefined;
  }
  return SAFE_BACKEND_ERROR_CODES.has(data.error.code) ? data.error.code : undefined;
}

async function callBackend(
  path: string,
  init: { method: "GET" | "POST"; token?: string; body?: unknown },
): Promise<BackendResult | undefined> {
  const baseUrl = configuredBackendUrl();
  if (!baseUrl) return undefined;

  const headers: Record<string, string> = { Accept: "application/json" };
  if (init.token) headers.Authorization = `Bearer ${init.token}`;
  if (init.body !== undefined) headers["Content-Type"] = "application/json";

  try {
    const requestInit: RequestInit = {
      method: init.method,
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    };
    if (init.body !== undefined) requestInit.body = JSON.stringify(init.body);
    const response = await fetch(`${baseUrl}${path}`, requestInit);
    let data: unknown;
    try {
      data = await response.json();
    } catch {
      data = undefined;
    }
    const result: BackendResult = {
      ok: response.ok,
      status: response.status,
      data,
    };
    const errorCode = canonicalErrorCode(data);
    if (errorCode) result.errorCode = errorCode;
    return result;
  } catch {
    return { ok: false, status: 503, data: undefined, errorCode: "DEPENDENCY_UNAVAILABLE" };
  }
}

function backendUnavailable(): NextResponse {
  return safeError(
    "BACKEND_UNAVAILABLE",
    "The onboarding service is temporarily unavailable.",
    503,
  );
}

function backendFailure(): NextResponse {
  return safeError(
    "BACKEND_REQUEST_FAILED",
    "The onboarding request could not be completed. Please try again.",
    502,
  );
}

function credentials(request: NextRequest): SessionCredentials | undefined {
  const sessionId = request.cookies.get(SESSION_ID_COOKIE)?.value;
  const token = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  return sessionId && token ? { sessionId, token } : undefined;
}

function isSession(value: unknown): value is SessionView {
  return (
    isRecord(value) &&
    typeof value.session_id === "string" &&
    UUID_PATTERN.test(value.session_id) &&
    value.session_type === "PSEUDONYMOUS" &&
    typeof value.status === "string" &&
    SESSION_STATUSES.has(value.status) &&
    typeof value.expires_at === "string" &&
    !Number.isNaN(Date.parse(value.expires_at)) &&
    (value.language_preference === undefined ||
      value.language_preference === null ||
      typeof value.language_preference === "string")
  );
}

function isCreatedSession(value: unknown): value is SessionView & { session_token: string } {
  return (
    isSession(value) &&
    "session_token" in value &&
    typeof value.session_token === "string" &&
    value.session_token.length >= 20 &&
    value.session_token.length <= 512 &&
    !/\s/.test(value.session_token)
  );
}

function safeSession(session: SessionView) {
  return {
    state: "ACTIVE",
    session_id: session.session_id,
    language_preference: session.language_preference ?? null,
    expires_at: session.expires_at,
  };
}

function sessionInvalid(result: BackendResult): boolean {
  return (
    result.status === 401 ||
    result.status === 404 ||
    result.status === 409 ||
    result.errorCode === "SESSION_EXPIRED" ||
    result.errorCode === "AUTHENTICATION_REQUIRED" ||
    result.errorCode === "INVALID_STATE_TRANSITION"
  );
}

async function readBody(request: NextRequest): Promise<unknown> {
  try {
    return await request.json();
  } catch {
    return undefined;
  }
}

export async function createSession(request: NextRequest): Promise<NextResponse> {
  const originError = rejectCrossOrigin(request);
  if (originError) return originError;

  const body = await readBody(request);
  const language = isRecord(body) ? body.language_preference : undefined;
  if (language !== "en" && language !== "hi") {
    return safeError("VALIDATION_ERROR", "Choose a supported session language.", 400);
  }

  const result = await callBackend("/api/v1/sessions", {
    method: "POST",
    body: { session_type: "PSEUDONYMOUS", language_preference: language },
  });
  if (!result) return backendUnavailable();
  if (!result.ok || !isCreatedSession(result.data) || result.data.status !== "ACTIVE") {
    return result.status === 503 ? backendUnavailable() : backendFailure();
  }

  const response = json(safeSession(result.data), 201);
  const options = sessionCookieOptions(requestHostname(request));
  response.cookies.set(SESSION_ID_COOKIE, result.data.session_id, options);
  response.cookies.set(SESSION_TOKEN_COOKIE, result.data.session_token, options);
  return response;
}

export async function readSession(request: NextRequest): Promise<NextResponse> {
  const current = credentials(request);
  if (!current) return json({ state: "NO_SESSION" });

  const result = await callBackend(`/api/v1/sessions/${encodeURIComponent(current.sessionId)}`, {
    method: "GET",
    token: current.token,
  });
  if (!result) return backendUnavailable();
  if (!result.ok) {
    if (sessionInvalid(result)) return clearSessionCookies(request, json({ state: "NO_SESSION" }));
    return result.status === 503 ? backendUnavailable() : backendFailure();
  }
  if (!isSession(result.data) || result.data.session_id !== current.sessionId)
    return backendFailure();
  if (result.data.status !== "ACTIVE") {
    return clearSessionCookies(request, json({ state: "NO_SESSION" }));
  }
  return json(safeSession(result.data));
}

export async function closeSession(request: NextRequest): Promise<NextResponse> {
  const originError = rejectCrossOrigin(request);
  if (originError) return originError;
  const current = credentials(request);
  if (!current) return clearSessionCookies(request, json({ state: "NO_SESSION" }));

  const result = await callBackend(
    `/api/v1/sessions/${encodeURIComponent(current.sessionId)}/close`,
    { method: "POST", token: current.token },
  );
  if (!result) return backendUnavailable();
  if (!result.ok) {
    if (sessionInvalid(result)) return clearSessionCookies(request, json({ state: "NO_SESSION" }));
    return result.status === 503 ? backendUnavailable() : backendFailure();
  }
  if (
    !isSession(result.data) ||
    result.data.session_id !== current.sessionId ||
    result.data.status !== "CLOSED"
  ) {
    return backendFailure();
  }
  return clearSessionCookies(request, json({ state: "CLOSED" }));
}

function consentListPath(sessionId: string): string {
  const query = new URLSearchParams({
    subject_type: "SESSION",
    subject_id: sessionId,
    purpose: PURPOSE,
  });
  return `/api/v1/consents?${query.toString()}`;
}

function isConsent(value: unknown): value is ConsentView {
  return (
    isRecord(value) &&
    typeof value.consent_id === "string" &&
    UUID_PATTERN.test(value.consent_id) &&
    value.subject_type === "SESSION" &&
    typeof value.subject_id === "string" &&
    UUID_PATTERN.test(value.subject_id) &&
    value.purpose === PURPOSE &&
    Array.isArray(value.scope) &&
    value.scope.every((item) => typeof item === "string") &&
    typeof value.notice_version === "string" &&
    typeof value.status === "string" &&
    CONSENT_STATUSES.has(value.status) &&
    typeof value.granted_at === "string" &&
    !Number.isNaN(Date.parse(value.granted_at))
  );
}

function isMatchingConsent(record: ConsentView, sessionId: string): boolean {
  return (
    record.subject_id === sessionId &&
    record.notice_version === NOTICE_VERSION &&
    record.scope.length === SCOPE.length &&
    record.scope.every((scope, index) => scope === SCOPE[index])
  );
}

function matchingConsents(value: unknown, sessionId: string): ConsentView[] | undefined {
  if (!Array.isArray(value) || !value.every(isConsent)) return undefined;
  return value.filter((record) => isMatchingConsent(record, sessionId));
}

const consentGrantLocks = new Map<string, Promise<void>>();

async function withConsentGrantLock<T>(sessionId: string, task: () => Promise<T>): Promise<T> {
  const previous = consentGrantLocks.get(sessionId) ?? Promise.resolve();
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  const queued = previous.then(() => gate);
  consentGrantLocks.set(sessionId, queued);
  await previous;
  try {
    return await task();
  } finally {
    release();
    if (consentGrantLocks.get(sessionId) === queued) consentGrantLocks.delete(sessionId);
  }
}

async function listConsents(current: SessionCredentials): Promise<BackendResult | undefined> {
  return callBackend(consentListPath(current.sessionId), {
    method: "GET",
    token: current.token,
  });
}

function safeConsent(record: ConsentView) {
  return {
    state: "GRANTED",
    notice_version: record.notice_version,
    granted_at: record.granted_at,
  };
}

function consentState(records: ConsentView[]) {
  const granted = records.find((record) => record.status === "GRANTED");
  if (granted) return safeConsent(granted);
  if (records.some((record) => record.status === "EXPIRED")) return { state: "EXPIRED" };
  if (records.some((record) => ["REVOKED", "SUPERSEDED"].includes(record.status))) {
    return { state: "REVOKED" };
  }
  return { state: "NOT_GRANTED" };
}

function consentSessionUnavailable(): NextResponse {
  return json({ state: "SESSION_UNAVAILABLE" });
}

export async function readConsent(request: NextRequest): Promise<NextResponse> {
  const current = credentials(request);
  if (!current) return consentSessionUnavailable();
  const result = await listConsents(current);
  if (!result) return backendUnavailable();
  if (!result.ok) {
    if (sessionInvalid(result)) {
      return clearSessionCookies(request, consentSessionUnavailable());
    }
    return result.status === 503 ? backendUnavailable() : backendFailure();
  }
  const records = matchingConsents(result.data, current.sessionId);
  return records ? json(consentState(records)) : backendFailure();
}

export async function grantConsent(request: NextRequest): Promise<NextResponse> {
  const originError = rejectCrossOrigin(request);
  if (originError) return originError;
  const current = credentials(request);
  if (!current) return consentSessionUnavailable();

  return withConsentGrantLock(current.sessionId, async () => {
    const existingResult = await listConsents(current);
    if (!existingResult) return backendUnavailable();
    if (!existingResult.ok) {
      if (sessionInvalid(existingResult)) {
        return clearSessionCookies(request, consentSessionUnavailable());
      }
      return existingResult.status === 503 ? backendUnavailable() : backendFailure();
    }
    const existing = matchingConsents(existingResult.data, current.sessionId);
    if (!existing) return backendFailure();
    const granted = existing.find((record) => record.status === "GRANTED");
    if (granted) return json(safeConsent(granted));

    const result = await callBackend("/api/v1/consents", {
      method: "POST",
      token: current.token,
      body: {
        subject_type: "SESSION",
        subject_id: current.sessionId,
        purpose: PURPOSE,
        scope: [...SCOPE],
        notice_version: NOTICE_VERSION,
      },
    });
    if (!result) return backendUnavailable();
    if (!result.ok) return result.status === 503 ? backendUnavailable() : backendFailure();
    if (
      !isConsent(result.data) ||
      !isMatchingConsent(result.data, current.sessionId) ||
      result.data.status !== "GRANTED"
    ) {
      return backendFailure();
    }
    return json(safeConsent(result.data), 201);
  });
}

export async function revokeConsent(request: NextRequest): Promise<NextResponse> {
  const originError = rejectCrossOrigin(request);
  if (originError) return originError;
  const current = credentials(request);
  if (!current) return consentSessionUnavailable();

  const existingResult = await listConsents(current);
  if (!existingResult) return backendUnavailable();
  if (!existingResult.ok) {
    if (sessionInvalid(existingResult)) {
      return clearSessionCookies(request, consentSessionUnavailable());
    }
    return existingResult.status === 503 ? backendUnavailable() : backendFailure();
  }
  const existing = matchingConsents(existingResult.data, current.sessionId);
  if (!existing) return backendFailure();
  const active = existing.filter((record) => record.status === "GRANTED");
  if (active.length === 0) return json({ state: "REVOKED" });

  for (const record of active) {
    const result = await callBackend(
      `/api/v1/consents/${encodeURIComponent(record.consent_id)}/revoke`,
      { method: "POST", token: current.token, body: { reason: "user_requested" } },
    );
    if (!result || !result.ok || !isConsent(result.data) || result.data.status !== "REVOKED") {
      return safeError(
        "CONSENT_WITHDRAWAL_FAILED",
        "Consent withdrawal could not be completed. Please try again.",
        502,
      );
    }
  }

  const verification = await listConsents(current);
  if (!verification?.ok) {
    return safeError(
      "CONSENT_WITHDRAWAL_FAILED",
      "Consent withdrawal could not be completed. Please try again.",
      502,
    );
  }
  const remaining = matchingConsents(verification.data, current.sessionId);
  if (!remaining || remaining.some((record) => record.status === "GRANTED")) {
    return safeError(
      "CONSENT_WITHDRAWAL_FAILED",
      "Consent withdrawal could not be completed. Please try again.",
      502,
    );
  }
  return json({ state: "REVOKED" });
}
