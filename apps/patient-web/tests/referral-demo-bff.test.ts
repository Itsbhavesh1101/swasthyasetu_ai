// @vitest-environment node

import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../app/api/engineering-demo/referral-discovery/route";
import { validEngineeringReferralDiscovery } from "../lib/referral-demo/server";

function result(overrides: Record<string, unknown> = {}) {
  return {
    classification: "ENGINEERING_SYNTHETIC",
    authority: "ENGINEERING_ONLY",
    route_disposition: "SYMBOLIC_MATCH",
    route_reason: "EXACT_SYMBOLIC_MATCH",
    service_code: "syn_service_college_demo",
    provider_display_name: "Synthetic College Demo Provider",
    provider_service_code: "syn_service_college_demo",
    provider_verification: "UNVERIFIED",
    resource_display_name: "Synthetic College Demo Resource",
    resource_code: "syn_resource_type_college_demo",
    resource_verification: "UNVERIFIED",
    source_verification: "UNVERIFIED",
    contacts_available: false,
    provider_selected: false,
    referral_state_model: "OFFERED",
    referral_created: false,
    sharing_consent: "NOT_REQUESTED",
    external_delivery: false,
    notification_delivery: false,
    notice:
      "Synthetic engineering preview only. Directory records are unverified, no provider is selected, no referral is created, and no data is shared or delivered.",
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("engineering referral discovery BFF", () => {
  it("accepts the exact no-effect contract without credentials or caching", async () => {
    vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000/");
    const backendFetch = vi.fn().mockResolvedValue(Response.json(result()));
    vi.stubGlobal("fetch", backendFetch);

    const response = await GET();

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(backendFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/engineering-demo/referral-discovery",
      expect.objectContaining({ headers: { Accept: "application/json" }, cache: "no-store" }),
    );
    expect(JSON.stringify(await response.json())).not.toContain("Authorization");
  });

  it.each([
    ["verified provider", { provider_verification: "VERIFIED" }],
    ["verified source", { source_verification: "VERIFIED" }],
    ["selected provider", { provider_selected: true }],
    ["created referral", { referral_created: true }],
    ["sharing consent", { sharing_consent: "GRANTED" }],
    ["external delivery", { external_delivery: true }],
    ["notification delivery", { notification_delivery: true }],
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
    expect(validEngineeringReferralDiscovery(result({ notice: "Synthetic preview ready." }))).toBe(
      false,
    );
  });
});
