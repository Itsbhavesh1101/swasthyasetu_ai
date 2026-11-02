// @vitest-environment node

import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../app/api/engineering-demo/mannsetu-preview/route";
import { validEngineeringMannSetuPreview } from "../lib/mannsetu-demo/server";

function result(overrides: Record<string, unknown> = {}) {
  return {
    classification: "ENGINEERING_SYNTHETIC",
    authority: "ENGINEERING_ONLY",
    verification: "UNVERIFIED",
    extraction_status: "SYNTHETIC_PARSED",
    extractor_signal: "SYN_MH_SIGNAL_ALPHA",
    backstop_outcome: "SYNTHETIC_MATCHED",
    backstop_signal: "SYN_MH_SIGNAL_DELTA",
    precedence: "SYNTHETIC_OVERRIDE",
    route: "SYNTHETIC_ROUTE_GAMMA",
    reason_code: "SYN_MH_POLICY_REASON_DELTA",
    policy_state: "TEST_ONLY_ENABLED",
    clinical_meaning_assigned: false,
    mental_health_assessment_performed: false,
    patient_data_processed: false,
    resource_contacts_available: false,
    referral_created: false,
    external_delivery: false,
    notice:
      "Synthetic engineering symbols only. No mental-health assessment is performed, no clinical meaning is assigned, and no resource, referral, or external delivery is available.",
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("engineering MannSetu preview BFF", () => {
  it("accepts the exact no-effect contract without credentials or caching", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(result()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET();

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/engineering-demo/mannsetu-preview",
      expect.objectContaining({ headers: { Accept: "application/json" }, cache: "no-store" }),
    );
    expect(JSON.stringify(await response.json())).not.toContain("Authorization");
  });

  it.each([
    ["clinical authority", { authority: "CLINICAL" }],
    ["verified result", { verification: "VERIFIED" }],
    ["clinical meaning", { clinical_meaning_assigned: true }],
    ["assessment", { mental_health_assessment_performed: true }],
    ["patient processing", { patient_data_processed: true }],
    ["resource", { resource_contacts_available: true }],
    ["referral", { referral_created: true }],
    ["delivery", { external_delivery: true }],
    ["contact", { phone_number: "+00-0000000" }],
  ])("rejects %s authority", async (_name, mutation) => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(result(mutation))));

    const response = await GET();

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: { code: "RESULT_UNAVAILABLE", message: "The engineering preview is unavailable." },
    });
  });

  it("rejects a notice that omits the negative guarantees", () => {
    expect(validEngineeringMannSetuPreview(result({ notice: "Synthetic preview ready." }))).toBe(
      false,
    );
  });
});
