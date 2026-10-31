import { render, screen } from "@testing-library/react";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

import {
  SyntheticReferralPreview,
  type SyntheticReferralPreviewState,
} from "./support/synthetic-referral-preview";

describe("P13-E isolated patient referral presentation fixture", () => {
  it.each([
    ["UNAVAILABLE", "Referral services are unavailable in this fixture."],
    ["UNKNOWN", "Referral status is unknown in this fixture."],
    ["FAILED", "A simulated referral operation failed. No delivery is claimed."],
  ] as const)("renders %s without a success or delivery claim", (state, message) => {
    const { container } = render(<SyntheticReferralPreview state={state} />);

    expect(screen.getByRole("status")).toHaveTextContent(message);
    expect(screen.getByText(/engineering test fixture only/i)).toBeVisible();
    expect(screen.getByText(/synthetic source only/i)).toBeVisible();
    expect(container).not.toHaveTextContent(/sent successfully|delivered|acknowledged|scheduled/i);
    expect(container.querySelector("a, button, input, form")).toBeNull();
  });

  it("accepts only the closed synthetic failure-state vocabulary", () => {
    const accepted: readonly SyntheticReferralPreviewState[] = ["UNAVAILABLE", "UNKNOWN", "FAILED"];
    expect(accepted).toHaveLength(3);
  });

  it("fails closed for a runtime value outside the typed vocabulary", () => {
    render(<SyntheticReferralPreview state={"DELIVERED" as SyntheticReferralPreviewState} />);

    expect(screen.getByRole("status")).toHaveTextContent(
      "Referral services are unavailable in this fixture.",
    );
    expect(screen.queryByText(/delivered successfully/i)).toBeNull();
  });

  it("contains no contact, destination, clinical, or actionable content", () => {
    const { container } = render(<SyntheticReferralPreview state="FAILED" />);
    const text = container.textContent ?? "";

    expect(text).not.toMatch(/\+?\d[\d\s()-]{6,}/);
    expect(text).not.toMatch(/doctor|clinic|hospital|specialty|book|call|email|address/i);
    expect(container.querySelector("a[href], [data-provider-id], [data-referral-id]")).toBeNull();
  });

  it("exists only under test support and is absent from production imports", () => {
    const appRoot = process.cwd();
    const fixtureSource = readFileSync(
      join(appRoot, "tests", "support", "synthetic-referral-preview.tsx"),
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

    expect(productionSource).not.toContain("SyntheticReferralPreview");
    expect(productionSource).not.toContain("synthetic-referral-preview");
    expect(fixtureSource).not.toMatch(
      /fetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|indexedDB/,
    );
  });
});
