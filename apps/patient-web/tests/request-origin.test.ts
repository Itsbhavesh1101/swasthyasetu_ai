import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { validateMutationOrigin } from "../lib/security/request-origin";

function request(url: string, origin?: string): NextRequest {
  return origin
    ? new NextRequest(url, { headers: { origin }, method: "POST" })
    : new NextRequest(url, { method: "POST" });
}

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("validateMutationOrigin", () => {
  it("requires an Origin header for every cookie-authenticated mutation", () => {
    expect(validateMutationOrigin(request("http://localhost:3000/api/example"))).toEqual({
      code: "ORIGIN_REJECTED",
      message: "This request origin is not allowed.",
      status: 403,
    });
  });

  it("accepts the exact local request origin and rejects lookalikes", () => {
    const local = request("http://localhost:3000/api/example", "http://localhost:3000");
    const lookalike = request(
      "http://localhost:3000/api/example",
      "http://localhost:3000.attacker.invalid",
    );

    expect(validateMutationOrigin(local)).toBeUndefined();
    expect(validateMutationOrigin(lookalike)?.code).toBe("ORIGIN_REJECTED");
  });

  it("uses the browser-facing Host for a non-production local proxy", () => {
    const proxied = new NextRequest("http://localhost:3100/api/example", {
      headers: { host: "127.0.0.1:3100", origin: "http://127.0.0.1:3100" },
      method: "POST",
    });

    expect(validateMutationOrigin(proxied)).toBeUndefined();
  });

  it("uses an exact configured public origin instead of client-controlled Host", () => {
    vi.stubEnv("SWASTHYASETU_PUBLIC_ORIGIN", "https://patient.example");

    const publicRequest = request(
      "http://internal-service:3000/api/example",
      "https://patient.example",
    );
    const internalOrigin = request(
      "http://internal-service:3000/api/example",
      "http://internal-service:3000",
    );

    expect(validateMutationOrigin(publicRequest)).toBeUndefined();
    expect(validateMutationOrigin(internalOrigin)?.code).toBe("ORIGIN_REJECTED");
  });

  it("fails closed for unsafe configured origins", () => {
    vi.stubEnv("SWASTHYASETU_PUBLIC_ORIGIN", "http://patient.example");

    expect(
      validateMutationOrigin(
        request("http://localhost:3000/api/example", "http://patient.example"),
      ),
    ).toEqual({
      code: "ORIGIN_CONFIGURATION_INVALID",
      message: "The application origin is not configured.",
      status: 503,
    });
  });

  it("fails closed when the production public origin is not configured", () => {
    vi.stubEnv("NODE_ENV", "production");

    expect(
      validateMutationOrigin(
        request("https://patient.example/api/example", "https://patient.example"),
      ),
    ).toMatchObject({ code: "ORIGIN_CONFIGURATION_INVALID", status: 503 });
  });
});
