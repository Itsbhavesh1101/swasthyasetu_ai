// @vitest-environment node

import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { GET, PATCH } from "../app/api/patient/profile/route";
import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../lib/onboarding/server";

const sessionId = "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1";
const patientId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";
const token = "private-patient-session-token";
const cookie = `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${token}`;

function request(method = "GET", body?: unknown, headers?: Record<string, string>) {
  const init = {
    method,
    headers: {
      cookie,
      ...(method === "PATCH" ? { origin: "http://localhost:3000" } : {}),
      ...headers,
    },
  };
  return new NextRequest(
    "http://localhost:3000/api/patient/profile",
    body === undefined ? init : { ...init, body: JSON.stringify(body) },
  );
}

function account() {
  return Response.json({
    patient_id: patientId,
    display_name: "Patient Demo",
    profile_complete: true,
  });
}

function profile(updatedAt = "2026-11-03T10:00:00Z") {
  return Response.json({
    patient_id: patientId,
    status: "ACTIVE",
    preferred_language: "en",
    demographics: {
      date_of_birth: "2000-01-02",
      age_years: null,
      administrative_sex: "female",
      gender_identity: null,
      pregnancy_status: null,
      location_context: "Delhi",
      height_cm: 165,
      weight_kg: 60,
      bmi: 22,
    },
    created_at: "2026-11-03T09:00:00Z",
    updated_at: updatedAt,
  });
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("patient profile BFF", () => {
  it("derives the patient path from the authenticated account and never returns the bearer", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backend = vi.fn().mockResolvedValueOnce(account()).mockResolvedValueOnce(profile());
    vi.stubGlobal("fetch", backend);

    const response = await GET(request());
    expect(response.status).toBe(200);
    const safeText = await response.clone().text();
    expect(await response.json()).toMatchObject({
      state: "AUTHENTICATED",
      profile: { patientId, preferredLanguage: "en" },
    });
    expect(safeText).not.toContain(token);
    expect(backend).toHaveBeenNthCalledWith(
      2,
      `http://127.0.0.1:8000/api/v1/patients/${patientId}`,
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: `Bearer ${token}` }),
      }),
    );
  });

  it("rejects cross-origin and unknown profile fields before backend access", async () => {
    const backend = vi.fn();
    vi.stubGlobal("fetch", backend);
    const crossOrigin = await PATCH(request("PATCH", {}, { origin: "https://attacker.invalid" }));
    expect(crossOrigin.status).toBe(403);
    const unknown = await PATCH(
      request("PATCH", {
        expectedUpdatedAt: "2026-11-03T10:00:00Z",
        preferredLanguage: "en",
        displayName: "Patient Demo",
        demographics: {
          dateOfBirth: null,
          administrativeSex: null,
          genderIdentity: null,
          pregnancyStatus: null,
          locationContext: null,
          heightCm: null,
          weightKg: null,
        },
        patientId: "attacker-controlled",
      }),
    );
    expect(unknown.status).toBe(400);
    expect(backend).not.toHaveBeenCalled();
  });

  it("maps the bounded update and surfaces stale writes without leaking backend details", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
    const backend = vi
      .fn()
      .mockResolvedValueOnce(account())
      .mockResolvedValueOnce(
        Response.json({ error: { code: "RESOURCE_CONFLICT", debug: token } }, { status: 409 }),
      );
    vi.stubGlobal("fetch", backend);
    const response = await PATCH(
      request("PATCH", {
        expectedUpdatedAt: "2026-11-03T10:00:00Z",
        preferredLanguage: "hi",
        demographics: {
          dateOfBirth: "2000-01-02",
          administrativeSex: "female",
          genderIdentity: null,
          pregnancyStatus: null,
          locationContext: "Delhi",
          heightCm: 165,
          weightKg: 60,
        },
        displayName: "Patient Demo",
      }),
    );
    expect(response.status).toBe(409);
    const text = await response.text();
    expect(text).toContain("changed in another window");
    expect(text).not.toContain(token);
    const forwarded = JSON.parse(String(backend.mock.calls[1]?.[1]?.body)) as Record<
      string,
      unknown
    >;
    expect(forwarded).not.toHaveProperty("patient_id");
    expect(forwarded).toMatchObject({ preferred_language: "hi" });
  });

  it("returns anonymous without backend access when credentials are absent", async () => {
    const backend = vi.fn();
    vi.stubGlobal("fetch", backend);
    const response = await GET(new NextRequest("http://localhost:3000/api/patient/profile"));
    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({ state: "ANONYMOUS" });
    expect(backend).not.toHaveBeenCalled();
  });
});
