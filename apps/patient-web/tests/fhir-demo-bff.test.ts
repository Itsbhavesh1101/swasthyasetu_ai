// @vitest-environment node

import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../app/api/engineering-demo/fhir-preview/route";
import { validEngineeringFHIRPreview } from "../lib/fhir-demo/server";

function result(overrides: Record<string, unknown> = {}) {
  return {
    classification: "ENGINEERING_SYNTHETIC",
    authority: "ENGINEERING_ONLY",
    verification: "UNVERIFIED",
    fhir_version: "4.0.1",
    mapping_direction: "EXPORT",
    mapping_state: "SYNTHETIC_EXPORT_PROJECTION",
    resource_type: "Observation",
    structural_validation: "SYNTHETIC_STRUCTURAL_PASS",
    profile_validation: "SYNTHETIC_UNAVAILABLE",
    profile_issue: "PROFILE_PACKAGE_UNAVAILABLE",
    fhir_payload_present: false,
    patient_data_processed: false,
    profile_conformance_claimed: false,
    exchange_authorized: false,
    external_transport: false,
    abdm_invoked: false,
    persistence_written: false,
    notice:
      "Synthetic engineering metadata only. Structural mechanics are not profile conformance, no FHIR payload or patient data is processed, and no exchange, external transport, ABDM integration, or persistence occurs.",
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("engineering FHIR preview BFF", () => {
  it("accepts the exact no-exchange contract without credentials or caching", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(result()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET();

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/engineering-demo/fhir-preview",
      expect.objectContaining({ headers: { Accept: "application/json" }, cache: "no-store" }),
    );
    expect(JSON.stringify(await response.json())).not.toContain("Authorization");
  });

  it.each([
    ["clinical authority", { authority: "CLINICAL" }],
    ["FHIR R5", { fhir_version: "5.0.0" }],
    ["Condition", { resource_type: "Condition" }],
    ["profile pass", { profile_validation: "SYNTHETIC_STRUCTURAL_PASS" }],
    ["conformance", { profile_conformance_claimed: true }],
    ["payload", { fhir_payload_present: true }],
    ["patient processing", { patient_data_processed: true }],
    ["exchange", { exchange_authorized: true }],
    ["transport", { external_transport: true }],
    ["ABDM", { abdm_invoked: true }],
    ["persistence", { persistence_written: true }],
    ["resource body", { resource: { resourceType: "Observation" } }],
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
    expect(validEngineeringFHIRPreview(result({ notice: "Synthetic FHIR preview ready." }))).toBe(
      false,
    );
  });
});
