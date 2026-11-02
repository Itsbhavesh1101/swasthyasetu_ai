// @vitest-environment node

import { afterEach, describe, expect, it, vi } from "vitest";

function result(overrides: Record<string, unknown> = {}) {
  return {
    classification: "ENGINEERING_SYNTHETIC",
    authority: "ENGINEERING_ONLY",
    verification: "UNVERIFIED",
    mode: "SYNTHETIC_OFFLINE_MOCK",
    operation: "SYNTHETIC_OPERATION_ALPHA",
    scripted_state: "SYNTHETIC_REJECTED",
    scripted_issue: "SYNTHETIC_REJECTED",
    unknown_state: "SYNTHETIC_UNAVAILABLE",
    unknown_issue: "SYNTHETIC_UNAVAILABLE",
    zero_egress: true,
    official_protocol_adopted: false,
    abha_identity_processed: false,
    consent_evaluated: false,
    fhir_payload_present: false,
    sandbox_connected: false,
    patient_data_processed: false,
    local_intake_accessed: false,
    local_intake_mutated: false,
    external_transport: false,
    persistence_written: false,
    notice:
      "Synthetic offline engineering tokens only. No official ABDM protocol or ABHA identity is used, no consent or FHIR payload is processed, and no sandbox, patient data, local intake, network transport, or persistence is accessed.",
    ...overrides,
  };
}

async function subjects() {
  try {
    const route = await import("../app/api/engineering-demo/abdm-preview/route");
    const server = await import("../lib/abdm-demo/server");
    return { GET: route.GET, valid: server.validEngineeringABDMPreview };
  } catch {
    expect.fail("engineering ABDM BFF is not implemented");
  }
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("engineering ABDM preview BFF", () => {
  it("accepts the exact zero-egress contract without credentials or caching", async () => {
    const { GET } = await subjects();
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(result()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET();

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/engineering-demo/abdm-preview",
      expect.objectContaining({ headers: { Accept: "application/json" }, cache: "no-store" }),
    );
    expect(JSON.stringify(await response.json())).not.toContain("Authorization");
  });

  it.each([
    ["official authority", { authority: "OFFICIAL" }],
    ["accepted result", { scripted_state: "SYNTHETIC_ACCEPTED" }],
    ["egress", { zero_egress: false }],
    ["protocol adoption", { official_protocol_adopted: true }],
    ["identity", { abha_identity_processed: true }],
    ["consent", { consent_evaluated: true }],
    ["FHIR payload", { fhir_payload_present: true }],
    ["sandbox", { sandbox_connected: true }],
    ["patient processing", { patient_data_processed: true }],
    ["intake access", { local_intake_accessed: true }],
    ["intake mutation", { local_intake_mutated: true }],
    ["transport", { external_transport: true }],
    ["persistence", { persistence_written: true }],
    ["identifier", { abha_id: "private-canary" }],
  ])("rejects %s claims", async (_name, mutation) => {
    const { GET } = await subjects();
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(result(mutation))));

    const response = await GET();

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: { code: "RESULT_UNAVAILABLE", message: "The engineering preview is unavailable." },
    });
  });

  it("rejects a notice that omits the negative guarantees", async () => {
    const { valid } = await subjects();

    expect(valid(result({ notice: "Synthetic ABDM preview ready." }))).toBe(false);
  });
});
