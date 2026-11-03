import { NextRequest, NextResponse } from "next/server";

import {
  SESSION_ID_COOKIE,
  SESSION_TOKEN_COOKIE,
  sessionCookieOptions,
} from "../onboarding/server";
import { validateMutationOrigin } from "../security/request-origin";

const TIMEOUT_MS = 5_000;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
type RecordValue = Record<string, unknown>;

function record(value: unknown): value is RecordValue {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function response(body: unknown, status = 200) {
  const value = NextResponse.json(body, { status });
  value.headers.set("Cache-Control", "no-store");
  return value;
}

function safeError(status: number, message: string) {
  return response({ error: { code: "ACCOUNT_REQUEST_FAILED", message } }, status);
}

function backendOrigin(): string | undefined {
  const configured = process.env.SWASTHYASETU_BACKEND_URL?.trim();
  if (!configured) return undefined;
  try {
    const url = new URL(configured);
    const loopback = ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
    if (
      (url.protocol !== "https:" && !(url.protocol === "http:" && loopback)) ||
      url.pathname !== "/" ||
      url.search ||
      url.hash ||
      url.username ||
      url.password
    )
      return undefined;
    return url.origin;
  } catch {
    return undefined;
  }
}

function hostname(request: NextRequest) {
  return request.nextUrl.hostname || undefined;
}

function credentials(request: NextRequest) {
  const sessionId = request.cookies.get(SESSION_ID_COOKIE)?.value;
  const token = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  return sessionId && token ? { sessionId, token } : undefined;
}

function clear(request: NextRequest, value: NextResponse) {
  const options = sessionCookieOptions(hostname(request));
  value.cookies.set(SESSION_ID_COOKIE, "", { ...options, maxAge: 0 });
  value.cookies.set(SESSION_TOKEN_COOKIE, "", { ...options, maxAge: 0 });
  return value;
}

async function backend(path: string, init: RequestInit) {
  const origin = backendOrigin();
  if (!origin) return undefined;
  try {
    return await fetch(`${origin}${path}`, {
      ...init,
      cache: "no-store",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    return undefined;
  }
}

async function jsonValue(value: Response): Promise<unknown> {
  try {
    return await value.json();
  } catch {
    return undefined;
  }
}

function validSession(
  value: unknown,
): value is { session_id: string; session_token: string; expires_at: string } {
  return (
    record(value) &&
    typeof value.session_id === "string" &&
    UUID.test(value.session_id) &&
    typeof value.session_token === "string" &&
    value.session_token.length >= 20 &&
    !/\s/.test(value.session_token) &&
    typeof value.expires_at === "string" &&
    !Number.isNaN(Date.parse(value.expires_at))
  );
}

async function authenticate(request: NextRequest, mode: "login" | "register") {
  const originFailure = validateMutationOrigin(request);
  if (originFailure)
    return response(
      { error: { code: originFailure.code, message: originFailure.message } },
      originFailure.status,
    );
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return safeError(400, "Check the information and try again.");
  }
  if (
    !record(body) ||
    typeof body.email !== "string" ||
    typeof body.password !== "string" ||
    Object.keys(body).some((key) => !["email", "password"].includes(key))
  )
    return safeError(400, "Check the information and try again.");
  const payload = { email: body.email, password: body.password };
  const result = await backend(`/api/v1/accounts/${mode}`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result) return safeError(503, "The account service is temporarily unavailable.");
  const data = await jsonValue(result);
  if (!result.ok || !validSession(data))
    return safeError(
      result.status === 401 ? 401 : 502,
      mode === "login"
        ? "We could not sign you in with those details."
        : "We could not create the account.",
    );
  let profileComplete = false;
  if (mode === "login") {
    const current = await backend("/api/v1/accounts/me", {
      method: "GET",
      headers: { Accept: "application/json", Authorization: `Bearer ${data.session_token}` },
    });
    const account = current ? await jsonValue(current) : undefined;
    if (!current?.ok || !record(account) || typeof account.profile_complete !== "boolean")
      return safeError(503, "Your account profile is temporarily unavailable.");
    profileComplete = account.profile_complete;
  }
  const value = response(
    { state: "AUTHENTICATED", profileComplete },
    mode === "register" ? 201 : 200,
  );
  const options = sessionCookieOptions(hostname(request));
  value.cookies.set(SESSION_ID_COOKIE, data.session_id, options);
  value.cookies.set(SESSION_TOKEN_COOKIE, data.session_token, options);
  return value;
}

export const registerAccount = (request: NextRequest) => authenticate(request, "register");
export const loginAccount = (request: NextRequest) => authenticate(request, "login");

export async function readAccount(request: NextRequest) {
  const current = credentials(request);
  if (!current) return response({ state: "ANONYMOUS" });
  const result = await backend("/api/v1/accounts/me", {
    method: "GET",
    headers: { Accept: "application/json", Authorization: `Bearer ${current.token}` },
  });
  if (!result) return safeError(503, "The account service is temporarily unavailable.");
  const data = await jsonValue(result);
  if (!result.ok)
    return result.status === 401
      ? clear(request, response({ state: "ANONYMOUS" }))
      : safeError(502, "The account could not be loaded.");
  if (
    !record(data) ||
    typeof data.patient_id !== "string" ||
    !UUID.test(data.patient_id) ||
    (data.display_name !== null && typeof data.display_name !== "string") ||
    typeof data.profile_complete !== "boolean"
  )
    return safeError(502, "The account could not be loaded.");
  return response({
    state: "AUTHENTICATED",
    displayName: data.display_name,
    patientId: data.patient_id,
    profileComplete: data.profile_complete,
  });
}

export async function logoutAccount(request: NextRequest) {
  const failure = validateMutationOrigin(request);
  if (failure)
    return response({ error: { code: failure.code, message: failure.message } }, failure.status);
  const current = credentials(request);
  if (!current) return clear(request, response({ state: "ANONYMOUS" }));
  const result = await backend("/api/v1/accounts/logout", {
    method: "POST",
    headers: { Authorization: `Bearer ${current.token}` },
  });
  if (!result) return safeError(503, "Sign out could not be completed.");
  if (!result.ok && result.status !== 401)
    return safeError(502, "Sign out could not be completed.");
  return clear(request, response({ state: "ANONYMOUS" }));
}
