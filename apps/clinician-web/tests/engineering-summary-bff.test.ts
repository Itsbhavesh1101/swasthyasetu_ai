// @vitest-environment node

import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../app/api/engineering-demo/summary-review/route";
import { validEngineeringSummaryResult } from "../lib/summary-demo/server";

const sectionNames = [
  "CHIEF_COMPLAINT",
  "HPI",
  "PAST_MEDICAL_HISTORY",
  "PAST_SURGICAL_HISTORY",
  "MEDICATIONS",
  "ALLERGIES",
  "FAMILY_HISTORY",
  "PERSONAL_HISTORY",
  "REVIEW_OF_SYSTEMS",
  "PRIOR_INVESTIGATIONS",
];

function result(overrides: Record<string, unknown> = {}) {
  return {
    status: "DRAFT",
    classification: "ENGINEERING_ONLY",
    review_state: "REVIEW_REQUIRED",
    freshness: "STALE",
    affected_sections: ["HPI"],
    drift_reasons: ["NEW_SOURCE"],
    source_count: 1,
    sections: sectionNames.map((section, index) => ({
      section,
      readiness: index === 0 ? "UNVERIFIED" : "UNKNOWN",
      assertions: index === 0 ? ["SYNTHETIC_REPORTED_COMPLAINT"] : [],
      source_kinds: index === 0 ? ["P7_PATIENT_REPORTED"] : [],
      conflict_review_required: false,
    })),
    source_access: "NOT_AUTHORIZED",
    can_edit: false,
    can_confirm: false,
    can_reject: false,
    external_egress: false,
    notice:
      "Synthetic engineering draft only. Missing sections are unknown, source drift requires review, and no clinical action is authorized.",
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("engineering summary BFF", () => {
  it("accepts the exact minimized contract without credentials or caching", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(result()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET();

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/engineering-demo/summary-review",
      expect.objectContaining({ headers: { Accept: "application/json" }, cache: "no-store" }),
    );
    expect(JSON.stringify(await response.json())).not.toContain("Authorization");
  });

  it.each([
    ["patient identifier", { patient_id: "private-canary" }],
    ["clinical authority", { classification: "CLINICAL" }],
    ["source authority", { source_access: "AUTHORIZED" }],
    ["confirmed status", { status: "CONFIRMED" }],
    ["confirmation control", { can_confirm: true }],
    ["editing control", { can_edit: true }],
    ["external processing", { external_egress: true }],
    ["freshness promotion", { freshness: "CURRENT" }],
    ["wrong drift", { drift_reasons: ["SOURCE_CHANGED"] }],
  ])("rejects %s", async (_name, mutation) => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(result(mutation))));

    const response = await GET();

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: { code: "RESULT_UNAVAILABLE", message: "The engineering preview is unavailable." },
    });
  });

  it("rejects reordered sections and incomplete negative guarantees", () => {
    const valid = result();
    expect(
      validEngineeringSummaryResult({
        ...valid,
        sections: [...(valid.sections as object[])].reverse(),
      }),
    ).toBe(false);
    expect(validEngineeringSummaryResult(result({ notice: "Synthetic draft ready." }))).toBe(false);
  });
});
