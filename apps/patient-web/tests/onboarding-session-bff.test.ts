// @vitest-environment node

import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { GET, POST } from "../app/api/onboarding/session/route";
import { POST as closeSession } from "../app/api/onboarding/session/close/route";
import {
  SESSION_ID_COOKIE,
  SESSION_TOKEN_COOKIE,
  sessionCookieOptions,
} from "../lib/onboarding/server";

const sessionId = "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1";
const bearer = "test-only-opaque-session-token";

function request(path: string, init: RequestInit & { cookie?: string } = {}): NextRequest {
  const headers = new Headers(init.headers);
  if (init.cookie) headers.set("cookie", init.cookie);
  const requestInit: { headers: Headers; method?: string; body?: BodyInit } = { headers };
  if (init.method) requestInit.method = init.method;
  if (init.body !== undefined && init.body !== null) requestInit.body = init.body;
  return new NextRequest(`http://localhost:3000${path}`, requestInit);
}

function backendSession(overrides: Record<string, unknown> = {}) {
  return {
    session_id: sessionId,
    session_type: "PSEUDONYMOUS",
    status: "ACTIVE",
    language_preference: "en",
    created_at: "2026-10-12T10:00:00Z",
    expires_at: "2026-10-12T11:00:00Z",
    closed_at: null,
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("session onboarding BFF", () => {
  it("creates only a pseudonymous backend session and never returns the bearer", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi
      .fn()
      .mockResolvedValue(
        Response.json({ ...backendSession(), session_token: bearer }, { status: 201 }),
      );
    vi.stubGlobal("fetch", backendFetch);

    const response = await POST(
      request("/api/onboarding/session", {
        method: "POST",
        headers: { "content-type": "application/json", origin: "http://localhost:3000" },
        body: JSON.stringify({
          language_preference: "en",
          session_type: "KIOSK",
          name: "must be ignored",
        }),
      }),
    );

    expect(response.status).toBe(201);
    expect(backendFetch).toHaveBeenCalledOnce();
    expect(backendFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/sessions",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          session_type: "PSEUDONYMOUS",
          language_preference: "en",
        }),
      }),
    );
    const body = await response.json();
    expect(body).toEqual({
      state: "ACTIVE",
      session_id: sessionId,
      language_preference: "en",
      expires_at: "2026-10-12T11:00:00Z",
    });
    expect(JSON.stringify(body)).not.toContain(bearer);

    const cookies = response.cookies.getAll();
    expect(cookies.map(({ name }) => name)).toEqual([SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE]);
    const setCookie = response.headers.getSetCookie().join(";");
    expect(setCookie).toContain("HttpOnly");
    expect(setCookie).toContain("SameSite=strict");
    expect(setCookie).toContain("Path=/");
    expect(setCookie).not.toMatch(/Max-Age|Expires/);
  });

  it("marks session cookies Secure in production and outside loopback development", () => {
    vi.stubEnv("NODE_ENV", "production");
    expect(sessionCookieOptions("localhost")).toMatchObject({
      httpOnly: true,
      sameSite: "strict",
      path: "/",
      secure: true,
    });
    expect(sessionCookieOptions()).not.toHaveProperty("expires");
    expect(sessionCookieOptions()).not.toHaveProperty("maxAge");

    vi.stubEnv("NODE_ENV", "test");
    expect(sessionCookieOptions("localhost").secure).toBe(false);
    expect(sessionCookieOptions("127.0.0.1").secure).toBe(false);
    expect(sessionCookieOptions("preview.example").secure).toBe(true);
  });

  it("forwards the bearer only in Authorization when reading a session", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(backendSession()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET(
      request("/api/onboarding/session", {
        cookie: `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`,
      }),
    );

    expect(response.status).toBe(200);
    expect(backendFetch).toHaveBeenCalledWith(
      `http://127.0.0.1:8000/api/v1/sessions/${sessionId}`,
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({ Authorization: `Bearer ${bearer}` }),
      }),
    );
    expect(JSON.stringify(await response.json())).not.toContain(bearer);
  });

  it.each([401, 409])("clears cookies for authoritative invalid status %s", async (status) => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          Response.json(
            { error: { code: "AUTHENTICATION_REQUIRED", message: "safe", request_id: "r" } },
            { status },
          ),
        ),
    );

    const response = await GET(
      request("/api/onboarding/session", {
        cookie: `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`,
      }),
    );

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ state: "NO_SESSION" });
    const setCookie = response.headers.getSetCookie().join(";");
    expect(setCookie).toContain(`${SESSION_ID_COOKIE}=`);
    expect(setCookie).toContain(`${SESSION_TOKEN_COOKIE}=`);
    expect(setCookie).toContain("Max-Age=0");
  });

  it("closes the backend session and clears both cookies", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backendFetch = vi
      .fn()
      .mockResolvedValue(Response.json(backendSession({ status: "CLOSED" })));
    vi.stubGlobal("fetch", backendFetch);

    const response = await closeSession(
      request("/api/onboarding/session/close", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
        cookie: `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`,
      }),
    );

    expect(backendFetch).toHaveBeenCalledWith(
      `http://127.0.0.1:8000/api/v1/sessions/${sessionId}/close`,
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: `Bearer ${bearer}` }),
      }),
    );
    expect(await response.json()).toEqual({ state: "CLOSED" });
    expect(response.headers.getSetCookie().join(";")).toContain("Max-Age=0");
  });

  it("rejects a cross-origin mutation before calling the backend", async () => {
    const backendFetch = vi.fn();
    vi.stubGlobal("fetch", backendFetch);

    const response = await POST(
      request("/api/onboarding/session", {
        method: "POST",
        headers: { "content-type": "application/json", origin: "https://attacker.invalid" },
        body: JSON.stringify({ language_preference: "en" }),
      }),
    );

    expect(response.status).toBe(403);
    expect(await response.json()).toEqual({
      error: { code: "ORIGIN_REJECTED", message: "This request origin is not allowed." },
    });
    expect(backendFetch).not.toHaveBeenCalled();
  });

  it("rejects a mutation with no Origin before calling the backend", async () => {
    const backendFetch = vi.fn();
    vi.stubGlobal("fetch", backendFetch);

    const response = await POST(
      request("/api/onboarding/session", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ language_preference: "en" }),
      }),
    );

    expect(response.status).toBe(403);
    expect(await response.json()).toEqual({
      error: { code: "ORIGIN_REJECTED", message: "This request origin is not allowed." },
    });
    expect(backendFetch).not.toHaveBeenCalled();
  });

  it("returns a safe 503 when backend configuration is missing", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "");
    const response = await POST(
      request("/api/onboarding/session", {
        method: "POST",
        headers: { "content-type": "application/json", origin: "http://localhost:3000" },
        body: JSON.stringify({ language_preference: "hi" }),
      }),
    );

    expect(response.status).toBe(503);
    expect(await response.json()).toEqual({
      error: {
        code: "BACKEND_UNAVAILABLE",
        message: "The onboarding service is temporarily unavailable.",
      },
    });
  });

  it("rejects non-loopback plaintext and non-origin backend URLs", async () => {
    const backendFetch = vi.fn();
    vi.stubGlobal("fetch", backendFetch);

    for (const configured of [
      "http://backend.internal:8000",
      "https://backend.example/api",
      "https://backend.example?target=other",
      "https://backend.example#fragment",
    ]) {
      vi.stubEnv("SWASTHYASETU_BACKEND_URL", configured);
      const response = await POST(
        request("/api/onboarding/session", {
          method: "POST",
          headers: { "content-type": "application/json", origin: "http://localhost:3000" },
          body: JSON.stringify({ language_preference: "en" }),
        }),
      );
      expect(response.status).toBe(503);
    }
    expect(backendFetch).not.toHaveBeenCalled();
  });

  it("rejects a session read whose backend identity does not match the cookie", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          Response.json(backendSession({ session_id: "4ac04bc2-8750-4e43-baf0-365f827a7e07" })),
        ),
    );

    const response = await GET(
      request("/api/onboarding/session", {
        cookie: `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`,
      }),
    );

    expect(response.status).toBe(502);
  });

  it("rejects malformed backend session metadata without setting cookies", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          Response.json(
            { ...backendSession({ session_id: "not-an-opaque-uuid" }), session_token: bearer },
            { status: 201 },
          ),
        ),
    );

    const response = await POST(
      request("/api/onboarding/session", {
        method: "POST",
        headers: { "content-type": "application/json", origin: "http://localhost:3000" },
        body: JSON.stringify({ language_preference: "en" }),
      }),
    );

    expect(response.status).toBe(502);
    expect(response.cookies.getAll()).toHaveLength(0);
    expect(JSON.stringify(await response.json())).not.toContain("not-an-opaque-uuid");
  });

  it("does not log or echo the bearer when a backend call fails", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error(`failure ${bearer}`)));
    const logSpies = [
      vi.spyOn(console, "log").mockImplementation(() => undefined),
      vi.spyOn(console, "warn").mockImplementation(() => undefined),
      vi.spyOn(console, "error").mockImplementation(() => undefined),
    ];

    const response = await GET(
      request("/api/onboarding/session", {
        cookie: `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`,
      }),
    );

    expect(response.status).toBe(503);
    expect(JSON.stringify(await response.json())).not.toContain(bearer);
    for (const spy of logSpies) expect(spy).not.toHaveBeenCalled();
  });
});
