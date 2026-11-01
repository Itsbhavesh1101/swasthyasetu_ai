import { render, screen } from "@testing-library/react";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

import {
  SyntheticAdminAuthorizationPreview,
  projectSyntheticAdminPresentation,
} from "./support/synthetic-admin-authorization-preview";

describe("P21-B isolated synthetic admin authorization presentation", () => {
  it.each([
    ["IDENTITY_UNAVAILABLE", "Identity unavailable", "No trusted synthetic identity is available."],
    ["MFA_REQUIRED", "MFA required", "Synthetic MFA evidence is absent."],
    ["SCOPE_DENIED", "Scope denied", "No exact synthetic scope match is available."],
    [
      "SYNTHETIC_CONTRACT_MATCH",
      "Synthetic contract match",
      "A test-only synthetic contract matched. Runtime access is not granted.",
    ],
    ["STALE_SNAPSHOT", "Snapshot stale", "Synthetic authorization evidence is stale."],
    ["PENDING_HUMAN_REVIEW", "Review pending", "Required human decisions remain pending."],
  ] as const)("renders %s without an action surface", (state, heading, detail) => {
    const { container } = render(
      <SyntheticAdminAuthorizationPreview environment="TEST" state={state} />,
    );

    expect(screen.getByRole("status")).toHaveTextContent(heading);
    expect(screen.getByRole("status")).toHaveTextContent(detail);
    expect(screen.getByText(/engineering test fixture only/i)).toBeVisible();
    expect(screen.getByText(/read-only/i)).toBeVisible();
    expect(container.querySelector("a, button, input, select, textarea, form")).toBeNull();
    expect(container).not.toHaveTextContent(
      /access granted|authorized|approved|successfully saved/i,
    );
  });

  it("fails closed for unknown environment or state values", () => {
    expect(
      projectSyntheticAdminPresentation({ environment: "PREVIEW", state: "MFA_VERIFIED" }),
    ).toEqual({
      detail: "Synthetic admin presentation is unavailable.",
      heading: "Unavailable",
      token: "UNAVAILABLE",
    });
    expect(
      projectSyntheticAdminPresentation({ environment: "TEST", state: "MFA_VERIFIED" }),
    ).toEqual({
      detail: "Synthetic admin presentation is unavailable.",
      heading: "Unavailable",
      token: "UNAVAILABLE",
    });
  });

  it.each(["STAGING", "PILOT", "PRODUCTION"])(
    "rejects %s before reading the state",
    (environment) => {
      const input = Object.create(null) as Record<string, unknown>;
      Object.defineProperty(input, "environment", { enumerable: true, value: environment });
      Object.defineProperty(input, "state", {
        enumerable: true,
        get: () => {
          throw new Error("state must not be inspected");
        },
      });

      expect(projectSyntheticAdminPresentation(input)).toEqual({
        detail: "Synthetic admin presentation is unavailable.",
        heading: "Unavailable",
        token: "UNAVAILABLE",
      });
    },
  );

  it("contains no actor, object, institution, source, contact, or governance evidence", () => {
    const { container } = render(
      <SyntheticAdminAuthorizationPreview environment="LOCAL" state="SYNTHETIC_CONTRACT_MATCH" />,
    );
    const text = container.textContent ?? "";

    expect(text).not.toMatch(
      /syn_admin_|actor[_ -]?id|object[_ -]?id|institution[_ -]?id|source[_ -]?id/i,
    );
    expect(text).not.toMatch(/https?:|email|phone|address|license|credential|token|secret/i);
    expect(
      container.querySelector("[data-actor-id], [data-object-id], [data-source-id]"),
    ).toBeNull();
  });

  it("exists only under test support and has no browser, network, or production import", () => {
    const appRoot = process.cwd();
    const fixtureSource = readFileSync(
      join(appRoot, "tests", "support", "synthetic-admin-authorization-preview.tsx"),
      "utf8",
    );
    const productionRoots = [
      join(appRoot, "app"),
      join(appRoot, "components"),
      join(appRoot, "lib"),
    ];
    const walk = (path: string): string[] =>
      existsSync(path)
        ? readdirSync(path).flatMap((entry) => {
            const candidate = join(path, entry);
            return statSync(candidate).isDirectory() ? walk(candidate) : [candidate];
          })
        : [];
    const productionSource = productionRoots
      .flatMap((root) => walk(root))
      .filter((path) => /\.(?:ts|tsx)$/.test(path))
      .map((path) => readFileSync(path, "utf8"))
      .join("\n");

    expect(productionSource).not.toContain("SyntheticAdminAuthorizationPreview");
    expect(productionSource).not.toContain("projectSyntheticAdminPresentation");
    expect(fixtureSource).not.toMatch(
      /fetch\s*\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|indexedDB|document\.cookie/,
    );
  });
});
