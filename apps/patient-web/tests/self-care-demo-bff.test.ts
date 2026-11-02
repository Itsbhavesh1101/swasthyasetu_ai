// @vitest-environment node

import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../app/api/engineering-demo/self-care-preview/route";
import { validEngineeringSelfCarePreview } from "../lib/self-care-demo/server";

function result(overrides: Record<string, unknown> = {}) {
  return {
    classification: "ENGINEERING_SYNTHETIC",
    authority: "ENGINEERING_ONLY",
    verification: "UNVERIFIED",
    knowledge_pack_state: "TEST_ONLY_UNAPPROVED",
    knowledge_item_review_state: "TEST_ONLY_UNAPPROVED",
    source_verification: "UNVERIFIED",
    placeholder_token: "SYNTHETIC_PLACEHOLDER_ALPHA",
    candidate_outcome: "SYNTHETIC_ENGINEERING_CANDIDATE",
    candidate_reason: "SYNTHETIC_RULE_MATCH",
    candidate_count: 1,
    blocked_outcome: "SYNTHETIC_BLOCKED",
    blocked_reason: "SYNTHETIC_SAFETY_BLOCK",
    blocked_candidate_count: 0,
    safety_block_preserved: true,
    clinical_eligibility_established: false,
    guidance_text_available: false,
    guidance_display_authorized: false,
    rag_invoked: false,
    patient_data_processed: false,
    external_delivery: false,
    notice:
      "Synthetic engineering placeholders only. No clinical eligibility is established, no guidance text is available or authorized for display, and no RAG, patient-data processing, or external delivery occurs.",
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("engineering self-care preview BFF", () => {
  it("accepts the exact no-effect contract without credentials or caching", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(result()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET();

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/engineering-demo/self-care-preview",
      expect.objectContaining({ headers: { Accept: "application/json" }, cache: "no-store" }),
    );
    expect(JSON.stringify(await response.json())).not.toContain("Authorization");
  });

  it.each([
    ["clinical authority", { authority: "CLINICAL" }],
    ["verified source", { source_verification: "VERIFIED" }],
    ["approved pack", { knowledge_pack_state: "APPROVED" }],
    ["safety downgrade", { safety_block_preserved: false }],
    ["clinical eligibility", { clinical_eligibility_established: true }],
    ["guidance text", { guidance_text_available: true }],
    ["display permission", { guidance_display_authorized: true }],
    ["RAG", { rag_invoked: true }],
    ["patient processing", { patient_data_processed: true }],
    ["delivery", { external_delivery: true }],
    ["remedy", { remedy: "private-canary" }],
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
    expect(validEngineeringSelfCarePreview(result({ notice: "Synthetic preview ready." }))).toBe(
      false,
    );
  });
});
