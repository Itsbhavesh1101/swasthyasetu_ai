// @vitest-environment node
import { NextRequest } from "next/server";
import { afterEach, expect, it, vi } from "vitest";

import { POST as POST_GUIDANCE } from "../app/api/guidance/route";
import { GET as GET_CONSENT } from "../app/api/guidance/consent/route";
import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../lib/onboarding/server";

const sessionId = "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1";
const bearer = "private-guidance-token";
const cookie = `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`;

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

it("maps exact guidance consent without exposing the bearer", async () => {
  vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      Response.json({
        active: true,
        notice_version: "external-ai-v1",
        scope: ["ayurvedic_guidance"],
      }),
    ),
  );
  const response = await GET_CONSENT(
    new NextRequest("http://localhost:3000/api/guidance/consent", {
      headers: { cookie },
    }),
  );
  const text = await response.text();
  expect(JSON.parse(text)).toEqual({
    state: "AUTHENTICATED",
    active: true,
    noticeVersion: "external-ai-v1",
    scope: ["ayurvedic_guidance"],
  });
  expect(text).not.toContain(bearer);
});

it("rejects a cross-origin guidance request before backend access", async () => {
  const backend = vi.fn();
  vi.stubGlobal("fetch", backend);
  const response = await POST_GUIDANCE(
    new NextRequest("http://localhost:3000/api/guidance", {
      method: "POST",
      headers: {
        cookie,
        origin: "https://attacker.invalid",
        "content-type": "application/json",
      },
      body: JSON.stringify({ question: "How can I support hydration?" }),
    }),
  );
  expect(response.status).toBe(403);
  expect(backend).not.toHaveBeenCalled();
});

it("returns only a validated grounded answer from one explicit submission", async () => {
  vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
  const backend = vi.fn().mockResolvedValue(
    Response.json({
      outcome: "ANSWERED",
      answer: "Gentle hydration habits may support general wellbeing.",
      citations: [{ title: "WHO", url: "https://who.int/advice" }],
      retrieved_at: "2026-11-03T12:00:00Z",
    }),
  );
  vi.stubGlobal("fetch", backend);
  const response = await POST_GUIDANCE(
    new NextRequest("http://localhost:3000/api/guidance", {
      method: "POST",
      headers: {
        cookie,
        origin: "http://localhost:3000",
        "content-type": "application/json",
      },
      body: JSON.stringify({ question: "How can I support hydration?" }),
    }),
  );
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({
    outcome: "ANSWERED",
    answer: "Gentle hydration habits may support general wellbeing.",
    citations: [{ title: "WHO", url: "https://who.int/advice" }],
    retrievedAt: "2026-11-03T12:00:00Z",
  });
  expect(backend).toHaveBeenCalledTimes(1);
});
