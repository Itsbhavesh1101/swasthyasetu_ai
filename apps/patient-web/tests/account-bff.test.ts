// @vitest-environment node

import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { POST as login } from "../app/api/account/login/route";
import { GET as me } from "../app/api/account/me/route";
import { POST as register } from "../app/api/account/register/route";
import { POST as logout } from "../app/api/account/logout/route";
import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../lib/onboarding/server";

const sessionId = "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1";
const patientId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";
const accountId = "3f0bb868-b00b-41c6-9335-f9c8b96ce7b3";
const bearer = "test-only-account-session-token";

function request(path: string, init: RequestInit & { cookie?: string } = {}) {
  const headers = new Headers(init.headers);
  if (init.cookie) headers.set("cookie", init.cookie);
  const requestInit: { headers: Headers; method?: string; body?: BodyInit } = { headers };
  if (init.method) requestInit.method = init.method;
  if (init.body !== undefined && init.body !== null) requestInit.body = init.body;
  return new NextRequest(`http://localhost:3000${path}`, requestInit);
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("account BFF", () => {
  it("rejects cross-origin registration before parsing or calling backend", async () => {
    const backend = vi.fn();
    vi.stubGlobal("fetch", backend);
    const response = await register(
      request("/api/account/register", {
        method: "POST",
        headers: { origin: "https://attacker.invalid" },
        body: "not-json",
      }),
    );
    expect(response.status).toBe(403);
    expect(backend).not.toHaveBeenCalled();
  });

  it("stores credentials only in strict HttpOnly cookies", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json({
          session_id: sessionId,
          session_token: bearer,
          expires_at: "2026-11-04T10:00:00Z",
        }),
      ),
    );
    const response = await register(
      request("/api/account/register", {
        method: "POST",
        headers: { origin: "http://localhost:3000", "content-type": "application/json" },
        body: JSON.stringify({
          name: "Patient Demo",
          email: "patient@example.com",
          password: "correct horse battery staple",
        }),
      }),
    );
    expect(response.status).toBe(201);
    const body = await response.json();
    expect(body).toEqual({ state: "AUTHENTICATED" });
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(JSON.stringify(body)).not.toContain(bearer);
    const cookies = response.headers.getSetCookie().join(";");
    expect(cookies).toContain("HttpOnly");
    expect(cookies).toContain("SameSite=strict");
    expect(cookies).toContain(`${SESSION_ID_COOKIE}=${sessionId}`);
    expect(cookies).toContain(`${SESSION_TOKEN_COOKIE}=${bearer}`);
  });

  it("forwards bearer server-side and clears invalid credentials", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backend = vi
      .fn()
      .mockResolvedValueOnce(
        Response.json({
          account_id: accountId,
          patient_id: patientId,
          email: "patient@example.com",
          display_name: "Patient Demo",
        }),
      )
      .mockResolvedValueOnce(
        Response.json({ error: { code: "AUTHENTICATION_REQUIRED" } }, { status: 401 }),
      );
    vi.stubGlobal("fetch", backend);
    const cookie = `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`;
    const current = await me(request("/api/account/me", { cookie }));
    expect(await current.json()).toEqual({
      state: "AUTHENTICATED",
      displayName: "Patient Demo",
      patientId,
    });
    expect(backend).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/accounts/me",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: `Bearer ${bearer}` }),
      }),
    );
    const invalid = await me(request("/api/account/me", { cookie }));
    expect(await invalid.json()).toEqual({ state: "ANONYMOUS" });
    expect(invalid.headers.getSetCookie().join(";")).toContain("Max-Age=0");
  });

  it("logs out authoritatively before clearing cookies", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backend = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", backend);
    const response = await logout(
      request("/api/account/logout", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
        cookie: `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`,
      }),
    );
    expect(backend).toHaveBeenCalledOnce();
    expect(await response.json()).toEqual({ state: "ANONYMOUS" });
    expect(response.headers.getSetCookie().join(";")).toContain("Max-Age=0");
  });

  it("maps malformed responses and timeouts without leaking credentials", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error(bearer)));
    const response = await login(
      request("/api/account/login", {
        method: "POST",
        headers: { origin: "http://localhost:3000", "content-type": "application/json" },
        body: JSON.stringify({ email: "patient@example.com", password: "valid password here" }),
      }),
    );
    expect(response.status).toBe(503);
    expect(await response.text()).not.toContain(bearer);
  });
});
