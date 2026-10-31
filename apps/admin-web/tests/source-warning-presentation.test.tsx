import { render, screen } from "@testing-library/react";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

import {
  SyntheticSourceWarningPreview,
  type SyntheticSourceWarningState,
} from "./support/synthetic-source-warning-preview";

describe("P13-E isolated admin source-warning fixture", () => {
  it.each([
    ["SOURCE_UNAVAILABLE", "Synthetic source evidence is unavailable."],
    ["SOURCE_UNVERIFIED", "Synthetic source evidence is unverified."],
    ["SOURCE_STALE", "Synthetic source evidence is stale."],
    ["SOURCE_REVOKED", "Synthetic source evidence is revoked."],
  ] as const)("renders %s as read-only and without authority", (state, message) => {
    const { container } = render(<SyntheticSourceWarningPreview state={state} />);

    expect(screen.getByRole("status")).toHaveTextContent(message);
    expect(screen.getByText(/engineering test fixture only/i)).toBeVisible();
    expect(screen.getByText(/read-only/i)).toBeVisible();
    expect(container).not.toHaveTextContent(
      /verified provider|approved|published|saved successfully/i,
    );
    expect(container.querySelector("a, button, input, form")).toBeNull();
  });

  it("accepts only the closed synthetic source-warning vocabulary", () => {
    const accepted: readonly SyntheticSourceWarningState[] = [
      "SOURCE_UNAVAILABLE",
      "SOURCE_UNVERIFIED",
      "SOURCE_STALE",
      "SOURCE_REVOKED",
    ];
    expect(accepted).toHaveLength(4);
  });

  it("fails closed for a runtime value outside the typed vocabulary", () => {
    render(
      <SyntheticSourceWarningPreview state={"SOURCE_VERIFIED" as SyntheticSourceWarningState} />,
    );

    expect(screen.getByRole("status")).toHaveTextContent(
      "Synthetic source evidence is unavailable.",
    );
    expect(screen.queryByText(/source verified|approved/i)).toBeNull();
  });

  it("contains no source evidence, contact, provider, or moderation action", () => {
    const { container } = render(<SyntheticSourceWarningPreview state="SOURCE_REVOKED" />);
    const text = container.textContent ?? "";

    expect(text).not.toMatch(/\+?\d[\d\s()-]{6,}/);
    expect(text).not.toMatch(/https?:|email|address|license|proof|approve|publish|suspend/i);
    expect(
      container.querySelector("[data-source-id], [data-provider-id], [data-evidence]"),
    ).toBeNull();
  });

  it("exists only under test support and is absent from production imports", () => {
    const appRoot = process.cwd();
    const fixtureSource = readFileSync(
      join(appRoot, "tests", "support", "synthetic-source-warning-preview.tsx"),
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

    expect(productionSource).not.toContain("SyntheticSourceWarningPreview");
    expect(productionSource).not.toContain("synthetic-source-warning-preview");
    expect(fixtureSource).not.toMatch(
      /fetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|indexedDB/,
    );
  });
});
