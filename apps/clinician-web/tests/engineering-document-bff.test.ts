// @vitest-environment node

import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../app/api/engineering-demo/document-review/route";
import { validEngineeringDocumentResult } from "../lib/document-demo/server";

function result(overrides: Record<string, unknown> = {}) {
  return {
    status: "NEEDS_REVIEW",
    classification: "ENGINEERING_ONLY",
    ingestion_disposition: "SYNTHETIC_COMPATIBLE",
    lifecycle: ["UPLOADED", "VALIDATING", "ACCEPTED", "QUEUED", "PROCESSING", "NEEDS_REVIEW"],
    processing_status: "SUCCEEDED",
    processed_pages: 1,
    provider: "engineering.fixture",
    external_egress: false,
    document_type: "LAB_REPORT",
    classification_disposition: "SELECTED",
    classification_reason: "EXACT_SYNTHETIC_LABEL",
    processor_id: "LabReportProcessor",
    processor_version: "v1",
    processor_disposition: "NOOP_ABSTAIN",
    candidate_disposition: "UNCONFIRMED",
    evidence_references: 1,
    structural_match: "STRUCTURALLY_MATCHED_UNCONFIRMED",
    source_access: "NOT_VERIFIED",
    confidence: "UNKNOWN",
    notice:
      "Synthetic engineering metadata only. No file was uploaded, no medical value was extracted, and no clinical decision was made.",
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("engineering document BFF", () => {
  it("accepts the exact minimized contract without credentials or caching", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(result()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET();

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/engineering-demo/document-review",
      expect.objectContaining({ headers: { Accept: "application/json" }, cache: "no-store" }),
    );
    expect(JSON.stringify(await response.json())).not.toContain("Authorization");
  });

  it.each([
    ["patient identifier", { patient_id: "private-canary" }],
    ["clinical authority", { classification: "CLINICAL" }],
    ["source authority", { source_access: "VERIFIED" }],
    ["confirmed candidate", { candidate_disposition: "CONFIRMED" }],
    ["external processing", { external_egress: true }],
    ["executable processor", { processor_disposition: "EXECUTED" }],
    ["skipped lifecycle state", { lifecycle: ["UPLOADED", "NEEDS_REVIEW"] }],
  ])("rejects %s", async (_name, mutation) => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(result(mutation))));

    const response = await GET();

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: { code: "RESULT_UNAVAILABLE", message: "The engineering preview is unavailable." },
    });
  });

  it("rejects an authority notice that omits the negative guarantees", () => {
    expect(validEngineeringDocumentResult(result({ notice: "Synthetic preview ready." }))).toBe(
      false,
    );
  });
});
