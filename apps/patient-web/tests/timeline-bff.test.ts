// @vitest-environment node
import { NextRequest } from "next/server";
import { afterEach, expect, it, vi } from "vitest";

import { GET } from "../app/api/patient/timeline/route";
import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../lib/onboarding/server";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

it("derives the patient subject from the account before loading the timeline", async () => {
  vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
  const patientId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";
  const backend = vi
    .fn()
    .mockResolvedValueOnce(Response.json({ patient_id: patientId }))
    .mockResolvedValueOnce(Response.json({ items: [], next_cursor: null }));
  vi.stubGlobal("fetch", backend);
  const response = await GET(
    new NextRequest("http://localhost:3000/api/patient/timeline", {
      headers: {
        cookie: `${SESSION_ID_COOKIE}=1f0bb868-b00b-41c6-9335-f9c8b96ce7b1; ${SESSION_TOKEN_COOKIE}=private-token`,
      },
    }),
  );
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({ state: "AUTHENTICATED", items: [] });
  expect(String(backend.mock.calls.at(1)?.[0])).toContain(`/patients/${patientId}/timeline`);
});
