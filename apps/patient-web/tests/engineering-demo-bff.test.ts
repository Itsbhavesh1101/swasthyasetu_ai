// @vitest-environment node

import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../app/api/engineering-demo/intakes/[intakeId]/result/route";
import { validEngineeringDemoResult } from "../lib/demo/server";

const intakeId = "3f0bb868-b00b-41c6-9335-f9c8b96ce7b3";
const encounterId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";

function result(overrides: Record<string, unknown> = {}) {
  return {
    intake_id: intakeId,
    encounter_id: encounterId,
    status: "SYNTHETIC_PREVIEW",
    classification: "ENGINEERING_ONLY",
    extracted_label: "SYNTHETIC_PAIN",
    verification_state: "AI_EXTRACTED_UNCONFIRMED",
    safety_decision: {
      route: "ROUTINE_CARE",
      reason_codes: ["SYNTHETIC_ROUTINE"],
      policy_id: "synthetic-physical-safety-metadata",
      policy_version: "engineering.1",
      requires_clarification: false,
      blocks_self_care: true,
      created_at: "2026-11-02T12:00:00Z",
    },
    summary_sections: [
      {
        section_id: "CHIEF_COMPLAINT",
        readiness: "UNVERIFIED",
        labels: ["SYNTHETIC_PAIN"],
        review_required: false,
      },
    ],
    notice: "Engineering test data only. This is not a diagnosis or medical assessment.",
    ...overrides,
  };
}

function request(): NextRequest {
  return new NextRequest(`http://localhost:3000/api/engineering-demo/intakes/${intakeId}/result`, {
    headers: { cookie: "swasthyasetu_session_token=server-only-demo-token" },
  });
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("engineering demo BFF", () => {
  it("keeps the bearer server-only and accepts the exact minimized contract", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(result()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET(request(), { params: Promise.resolve({ intakeId }) });

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenCalledWith(
      `http://127.0.0.1:8000/api/v1/engineering-demo/intakes/${intakeId}/result`,
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer server-only-demo-token" }),
      }),
    );
    expect(JSON.stringify(await response.json())).not.toContain("server-only-demo-token");
  });

  it.each([
    ["patient identifier", { patient_id: "private-canary" }],
    ["unknown route", { safety_decision: { ...result().safety_decision, route: "CLEARED" } }],
    [
      "inconsistent route flags",
      { safety_decision: { ...result().safety_decision, blocks_self_care: false } },
    ],
    [
      "duplicate reasons",
      {
        safety_decision: {
          ...result().safety_decision,
          reason_codes: ["SYNTHETIC_ROUTINE", "SYNTHETIC_ROUTINE"],
        },
      },
    ],
    ["forged clinical label", { extracted_label: "DIAGNOSIS" }],
    ["preview without a source-backed section", { summary_sections: [] }],
    [
      "forged summary review state",
      {
        summary_sections: [
          {
            section_id: "CHIEF_COMPLAINT",
            readiness: "UNVERIFIED",
            labels: ["SYNTHETIC_PAIN"],
            review_required: true,
          },
        ],
      },
    ],
  ])("rejects %s from the backend", async (_name, mutation) => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(result(mutation))));

    const response = await GET(request(), { params: Promise.resolve({ intakeId }) });

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: { code: "RESULT_UNAVAILABLE", message: "The synthetic preview is unavailable." },
    });
  });

  it("requires exact abstention emptiness", () => {
    expect(
      validEngineeringDemoResult(
        result({
          status: "ABSTAINED",
          extracted_label: null,
          verification_state: null,
          safety_decision: null,
          summary_sections: [],
        }),
      ),
    ).toBe(true);
  });
});
