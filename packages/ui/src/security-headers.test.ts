import { describe, expect, it } from "vitest";

import { browserSecurityHeaders } from "./security-headers";

function values(production: boolean): Map<string, string> {
  return new Map(browserSecurityHeaders(production).map(({ key, value }) => [key, value]));
}

describe("browserSecurityHeaders", () => {
  it("uses a production CSP without eval and enables transport pinning", () => {
    const headers = values(true);
    const csp = headers.get("Content-Security-Policy") ?? "";

    expect(csp).toContain("default-src 'self'");
    expect(csp).toContain("frame-ancestors 'none'");
    expect(csp).toContain("object-src 'none'");
    expect(csp).toContain("connect-src 'self'");
    expect(csp).toContain("upgrade-insecure-requests");
    expect(csp).not.toContain("'unsafe-eval'");
    expect(headers.get("Strict-Transport-Security")).toBe("max-age=31536000; includeSubDomains");
  });

  it("permits only development tooling exceptions outside production", () => {
    const headers = values(false);
    const csp = headers.get("Content-Security-Policy") ?? "";

    expect(csp).toContain("script-src 'self' 'unsafe-inline' 'unsafe-eval'");
    expect(csp).toContain("connect-src 'self' ws: wss:");
    expect(headers.has("Strict-Transport-Security")).toBe(false);
    expect(headers.get("X-Content-Type-Options")).toBe("nosniff");
    expect(headers.get("X-Frame-Options")).toBe("DENY");
    expect(headers.get("Referrer-Policy")).toBe("no-referrer");
  });
});
