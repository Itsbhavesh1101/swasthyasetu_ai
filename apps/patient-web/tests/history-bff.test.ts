// @vitest-environment node

import { NextRequest } from "next/server";
import { afterEach, expect, it, vi } from "vitest";

import { GET, POST as add } from "../app/api/patient/history/route";
import { POST as supersede } from "../app/api/patient/history/[factId]/supersede/route";
import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../lib/onboarding/server";

const sessionId = "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1";
const patientId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";
const factId = "3f0bb868-b00b-41c6-9335-f9c8b96ce7b3";
const replacementId = "4f0bb868-b00b-41c6-9335-f9c8b96ce7b4";
const token = "private-history-session-token";
const cookie = `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${token}`;

function request(path: string, method = "GET", body?: unknown, origin = "http://localhost:3000") {
  const init = { method, headers: { cookie, ...(method === "POST" ? { origin } : {}) } };
  return new NextRequest(
    `http://localhost:3000${path}`,
    body === undefined ? init : { ...init, body: JSON.stringify(body) },
  );
}

function account() {
  return Response.json({ patient_id: patientId });
}

function fact(id = factId, label = "Synthetic condition") {
  return {
    fact_id: id,
    fact_type: "PROBLEM",
    canonical_label: label,
    effective_time: null,
    recorded_at: "2026-11-03T13:00:00Z",
    verification_state: "PATIENT_CONFIRMED",
    status: "ACTIVE",
    superseded_by_fact_id: null,
    provenance: {
      source_type: "PATIENT_REPORT",
      confidence: null,
      created_at: "2026-11-03T13:00:00Z",
    },
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

it("lists a bounded self-owned history without exposing the bearer", async () => {
  vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
  const backend = vi
    .fn()
    .mockResolvedValueOnce(account())
    .mockResolvedValueOnce(Response.json({ items: [fact()], next_cursor: null }));
  vi.stubGlobal("fetch", backend);
  const response = await GET(request("/api/patient/history"));
  const safeText = await response.clone().text();
  expect(await response.json()).toMatchObject({
    state: "AUTHENTICATED",
    items: [{ factId, label: "Synthetic condition" }],
  });
  expect(safeText).not.toContain(token);
  expect(backend).toHaveBeenNthCalledWith(
    2,
    `http://127.0.0.1:8000/api/v1/patients/${patientId}/facts?limit=100`,
    expect.objectContaining({
      headers: expect.objectContaining({ Authorization: `Bearer ${token}` }),
    }),
  );
});

it("rejects cross-origin and unknown history fields before account lookup", async () => {
  const backend = vi.fn();
  vi.stubGlobal("fetch", backend);
  const cross = await add(
    request(
      "/api/patient/history",
      "POST",
      { fact_type: "PROBLEM", label: "Synthetic", status: "ACTIVE" },
      "https://attacker.invalid",
    ),
  );
  const unknown = await add(
    request("/api/patient/history", "POST", {
      fact_type: "PROBLEM",
      label: "Synthetic",
      status: "ACTIVE",
      patient_id: patientId,
    }),
  );
  expect(cross.status).toBe(403);
  expect(unknown.status).toBe(400);
  expect(backend).not.toHaveBeenCalled();
});

it("derives create and correction paths and wraps the exact expected fact", async () => {
  vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
  const payload = { fact_type: "PROBLEM", label: "Synthetic", status: "ACTIVE" };
  const backend = vi
    .fn()
    .mockResolvedValueOnce(account())
    .mockResolvedValueOnce(Response.json(fact(), { status: 201 }))
    .mockResolvedValueOnce(account())
    .mockResolvedValueOnce(
      Response.json({
        superseded: {
          ...fact(),
          verification_state: "SUPERSEDED",
          superseded_by_fact_id: replacementId,
        },
        replacement: fact(replacementId, "Synthetic corrected"),
      }),
    );
  vi.stubGlobal("fetch", backend);
  expect((await add(request("/api/patient/history", "POST", payload))).status).toBe(201);
  const corrected = await supersede(
    request(`/api/patient/history/${factId}/supersede`, "POST", payload),
    {
      params: Promise.resolve({ factId }),
    },
  );
  expect(corrected.status).toBe(200);
  expect(backend.mock.calls[1]?.[0]).toContain(`/patients/${patientId}/facts`);
  expect(backend.mock.calls[3]?.[0]).toContain(`/facts/${factId}/supersede`);
  expect(JSON.parse(String(backend.mock.calls[3]?.[1]?.body))).toEqual({
    expected_current_id: factId,
    replacement: payload,
  });
});
