// @vitest-environment node

import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { POST as start } from "../app/api/intake/start/route";
import { GET as read } from "../app/api/intake/[intakeId]/route";
import { POST as answer } from "../app/api/intake/[intakeId]/answers/route";

const sessionId = "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1";
const encounterId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";
const intakeId = "3f0bb868-b00b-41c6-9335-f9c8b96ce7b3";
const bearer = "test-only-opaque-session-token";

function request(path: string, init: RequestInit = {}): NextRequest {
  const headers = new Headers(init.headers);
  headers.set(
    "cookie",
    `swasthyasetu_session_id=${sessionId}; swasthyasetu_session_token=${bearer}`,
  );
  const requestInit: { headers: Headers; method?: string; body?: BodyInit } = { headers };
  if (init.method) requestInit.method = init.method;
  if (init.body !== undefined && init.body !== null) requestInit.body = init.body;
  return new NextRequest(`http://localhost:3000${path}`, requestInit);
}

function view(overrides: Record<string, unknown> = {}) {
  return {
    intake_id: intakeId,
    encounter_id: encounterId,
    status: "IN_PROGRESS",
    version: 1,
    started_at: "2026-10-18T00:00:00Z",
    completed_at: null,
    pack_versions: [{ pack_id: "core.intake", pack_version: "engineering.1" }],
    current_question: {
      question_id: "core.chief_complaint",
      question_version: "engineering.1",
      pack_id: "core.intake",
      pack_version: "engineering.1",
      section: "CHIEF_COMPLAINT",
      prompt: "Synthetic prompt",
      help_text: null,
      answer_type: "TEXT",
      requiredness: "REQUIRED",
      allow_unknown: false,
      allow_prefer_not_to_answer: false,
      allow_skip: false,
      constraints: { min_length: 1, max_length: 500 },
      options: [],
    },
    engine_state: "NEXT_QUESTION",
    completion_ready: false,
    answers: [],
    missing_information: [
      {
        field_or_question_key: "core.chief_complaint",
        reason_code: "REQUIRED_UNANSWERED",
        requiredness: "REQUIRED",
      },
    ],
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("clinical intake BFF", () => {
  it("keeps the bearer server-only while finding an encounter and starting intake", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi
      .fn()
      .mockResolvedValueOnce(Response.json({ encounter_id: encounterId }))
      .mockResolvedValueOnce(Response.json(view(), { status: 201 }));
    vi.stubGlobal("fetch", backendFetch);

    const response = await start(
      request("/api/intake/start", {
        method: "POST",
        headers: { origin: "http://localhost:3000" },
      }),
    );
    expect(response.status).toBe(201);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenNthCalledWith(
      1,
      "http://127.0.0.1:8000/api/v1/encounters/general-intake",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ session_id: sessionId }),
        headers: expect.objectContaining({ Authorization: `Bearer ${bearer}` }),
      }),
    );
    expect(backendFetch).toHaveBeenNthCalledWith(
      2,
      `http://127.0.0.1:8000/api/v1/encounters/${encounterId}/intake`,
      expect.objectContaining({ body: JSON.stringify({ pack_ids: ["core.intake"] }) }),
    );
    expect(JSON.stringify(await response.json())).not.toContain(bearer);
  });

  it("rejects malformed extra backend data instead of exposing it", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(view({ secret: "no" }))));
    const response = await read(request(`/api/intake/${intakeId}`), {
      params: Promise.resolve({ intakeId }),
    });
    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: {
        code: "INVALID_BACKEND_RESPONSE",
        message: "The intake response could not be verified.",
      },
    });
  });

  it("rejects cross-origin answers before any backend request", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn();
    vi.stubGlobal("fetch", backendFetch);
    const response = await answer(
      request(`/api/intake/${intakeId}/answers`, {
        method: "POST",
        headers: { origin: "https://attacker.invalid", "content-type": "application/json" },
        body: JSON.stringify({ expected_version: 1 }),
      }),
      { params: Promise.resolve({ intakeId }) },
    );
    expect(response.status).toBe(403);
    expect(backendFetch).not.toHaveBeenCalled();
  });
});
