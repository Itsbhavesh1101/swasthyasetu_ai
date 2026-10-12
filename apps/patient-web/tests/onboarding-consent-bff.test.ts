// @vitest-environment node

import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { GET, POST } from "../app/api/onboarding/consent/route";
import { POST as revokeConsent } from "../app/api/onboarding/consent/revoke/route";
import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../lib/onboarding/server";

const sessionId = "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1";
const consentId = "a81df776-46ca-4ba4-a044-c5db19fc0075";
const secondConsentId = "3e4d02db-97a6-4cb3-af0d-91fdebe3f47f";
const bearer = "test-only-consent-bearer";

function request(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("cookie", `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`);
  const requestInit: { headers: Headers; method?: string; body?: BodyInit } = { headers };
  if (init.method) requestInit.method = init.method;
  if (init.body !== undefined && init.body !== null) requestInit.body = init.body;
  return new NextRequest(`http://localhost:3000${path}`, requestInit);
}

function consent(id = consentId, status = "GRANTED") {
  return {
    consent_id: id,
    subject_type: "SESSION",
    subject_id: sessionId,
    purpose: "GENERAL_PRODUCT_USE",
    scope: ["clinical_intake"],
    notice_version: "privacy-v1",
    status,
    granted_at: "2026-10-12T10:00:00Z",
    revoked_at: status === "REVOKED" ? "2026-10-12T10:05:00Z" : null,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("consent onboarding BFF", () => {
  it("derives every consent authority field server-side", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backendFetch = vi
      .fn()
      .mockResolvedValueOnce(Response.json([]))
      .mockResolvedValueOnce(Response.json(consent(), { status: 201 }));
    vi.stubGlobal("fetch", backendFetch);

    const response = await POST(
      request("/api/onboarding/consent", {
        method: "POST",
        headers: { "content-type": "application/json", origin: "http://localhost:3000" },
        body: JSON.stringify({
          subject_type: "PATIENT",
          subject_id: "attacker-controlled",
          purpose: "RESEARCH_USE",
          scope: ["everything"],
          notice_version: "attacker-version",
        }),
      }),
    );

    expect(response.status).toBe(201);
    expect(backendFetch).toHaveBeenNthCalledWith(
      2,
      "http://127.0.0.1:8000/api/v1/consents",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: `Bearer ${bearer}` }),
        body: JSON.stringify({
          subject_type: "SESSION",
          subject_id: sessionId,
          purpose: "GENERAL_PRODUCT_USE",
          scope: ["clinical_intake"],
          notice_version: "privacy-v1",
        }),
      }),
    );
    expect(await response.json()).toEqual({
      state: "GRANTED",
      notice_version: "privacy-v1",
      granted_at: "2026-10-12T10:00:00Z",
    });
  });

  it("returns an existing active matching grant without creating a duplicate", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backendFetch = vi.fn().mockResolvedValue(Response.json([consent()]));
    vi.stubGlobal("fetch", backendFetch);

    const response = await POST(
      request("/api/onboarding/consent", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
      }),
    );

    expect(response.status).toBe(200);
    expect(backendFetch).toHaveBeenCalledOnce();
    expect(await response.json()).toMatchObject({ state: "GRANTED" });
  });

  it("does not treat a differently scoped grant as the controlled onboarding consent", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backendFetch = vi
      .fn()
      .mockResolvedValueOnce(
        Response.json([{ ...consent(), scope: ["clinical_intake", "research_export"] }]),
      )
      .mockResolvedValueOnce(Response.json(consent(), { status: 201 }));
    vi.stubGlobal("fetch", backendFetch);

    const response = await POST(
      request("/api/onboarding/consent", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
      }),
    );

    expect(response.status).toBe(201);
    expect(backendFetch).toHaveBeenCalledTimes(2);
  });

  it("serializes concurrent grants for the same session", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    let created = false;
    const backendFetch = vi.fn(async (_url: string, init: RequestInit) => {
      if (init.method === "GET") return Response.json(created ? [consent()] : []);
      created = true;
      return Response.json(consent(), { status: 201 });
    });
    vi.stubGlobal("fetch", backendFetch);
    const makeRequest = () =>
      request("/api/onboarding/consent", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
      });

    const responses = await Promise.all([POST(makeRequest()), POST(makeRequest())]);

    expect(responses.map(({ status }) => status).sort()).toEqual([200, 201]);
    expect(
      backendFetch.mock.calls.filter(([, init]) => (init as RequestInit).method === "POST"),
    ).toHaveLength(1);
  });

  it("rejects a grant response that does not match controlled consent fields", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(Response.json([]))
        .mockResolvedValueOnce(
          Response.json({ ...consent(), notice_version: "unexpected-v2" }, { status: 201 }),
        ),
    );

    const response = await POST(
      request("/api/onboarding/consent", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
      }),
    );

    expect(response.status).toBe(502);
    expect(JSON.stringify(await response.json())).not.toContain("unexpected-v2");
  });

  it("returns only a minimized consent status", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json([consent()])));

    const response = await GET(request("/api/onboarding/consent"));
    const body = await response.json();

    expect(body).toEqual({
      state: "GRANTED",
      notice_version: "privacy-v1",
      granted_at: "2026-10-12T10:00:00Z",
    });
    expect(JSON.stringify(body)).not.toContain(consentId);
    expect(JSON.stringify(body)).not.toContain(bearer);
  });

  it("rejects an unrecognized backend consent status", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(Response.json([consent(consentId, "UNRECOGNIZED")])),
    );

    const response = await GET(request("/api/onboarding/consent"));

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: {
        code: "BACKEND_REQUEST_FAILED",
        message: "The onboarding request could not be completed. Please try again.",
      },
    });
  });

  it("revokes every active matching grant using the controlled reason", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backendFetch = vi
      .fn()
      .mockResolvedValueOnce(Response.json([consent(), consent(secondConsentId)]))
      .mockResolvedValueOnce(Response.json(consent(consentId, "REVOKED")))
      .mockResolvedValueOnce(Response.json(consent(secondConsentId, "REVOKED")))
      .mockResolvedValueOnce(
        Response.json([consent(consentId, "REVOKED"), consent(secondConsentId, "REVOKED")]),
      );
    vi.stubGlobal("fetch", backendFetch);

    const response = await revokeConsent(
      request("/api/onboarding/consent/revoke", {
        method: "POST",
        headers: { "content-type": "application/json", origin: "http://localhost:3000" },
        body: JSON.stringify({ reason: "attacker_reason" }),
      }),
    );

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ state: "REVOKED" });
    for (const id of [consentId, secondConsentId]) {
      expect(backendFetch).toHaveBeenCalledWith(
        `http://127.0.0.1:8000/api/v1/consents/${id}/revoke`,
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ reason: "user_requested" }),
        }),
      );
    }
  });

  it("surfaces failure and never claims withdrawal when any matching grant remains", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backendFetch = vi
      .fn()
      .mockResolvedValueOnce(Response.json([consent(), consent(secondConsentId)]))
      .mockResolvedValueOnce(Response.json(consent(consentId, "REVOKED")))
      .mockResolvedValueOnce(
        Response.json(
          { error: { code: "PROCESSING_FAILED", message: "raw", request_id: "r" } },
          { status: 500 },
        ),
      );
    vi.stubGlobal("fetch", backendFetch);

    const response = await revokeConsent(
      request("/api/onboarding/consent/revoke", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
      }),
    );

    expect(response.status).toBe(502);
    const body = await response.json();
    expect(body).toEqual({
      error: {
        code: "CONSENT_WITHDRAWAL_FAILED",
        message: "Consent withdrawal could not be completed. Please try again.",
      },
    });
    expect(body).not.toHaveProperty("state", "REVOKED");
    expect(JSON.stringify(body)).not.toContain('"message":"raw"');
  });

  it("clears stale cookies when revoke discovers an invalid session", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          Response.json(
            { error: { code: "SESSION_EXPIRED", message: "safe", request_id: "r" } },
            { status: 401 },
          ),
        ),
    );

    const response = await revokeConsent(
      request("/api/onboarding/consent/revoke", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
      }),
    );

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ state: "SESSION_UNAVAILABLE" });
    expect(response.headers.getSetCookie().join(";")).toContain("Max-Age=0");
  });
});
