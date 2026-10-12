// @vitest-environment node

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const applicationRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const styles = readFileSync(join(applicationRoot, "app", "globals.css"), "utf8");

function channel(value: number): number {
  const normalized = value / 255;
  return normalized <= 0.04045 ? normalized / 12.92 : Math.pow((normalized + 0.055) / 1.055, 2.4);
}

function luminance(hex: string): number {
  const value = Number.parseInt(hex.slice(1), 16);
  return (
    0.2126 * channel((value >> 16) & 255) +
    0.7152 * channel((value >> 8) & 255) +
    0.0722 * channel(value & 255)
  );
}

function contrast(first: string, second: string): number {
  const values = [luminance(first), luminance(second)].sort((a, b) => b - a);
  return (values[0]! + 0.05) / (values[1]! + 0.05);
}

describe("P6-C deterministic accessibility baseline", () => {
  it.each([
    ["main text on canvas", "#17221d", "#f5f7f2", 4.5],
    ["main text on surface", "#17221d", "#ffffff", 4.5],
    ["muted text on surface", "#526159", "#ffffff", 4.5],
    ["primary button", "#ffffff", "#176448", 4.5],
    ["critical button", "#ffffff", "#a52a2a", 4.5],
    ["focus indicator", "#7a4b00", "#ffffff", 3],
    ["disabled control", "#5c665f", "#e6eae7", 4.5],
  ])("passes contrast for %s", (_label, foreground, background, minimum) => {
    expect(contrast(foreground, background)).toBeGreaterThanOrEqual(minimum);
  });

  it("preserves touch, reduced-motion, focus, and forced-color rules", () => {
    expect(styles).toContain("--patient-touch: 2.75rem");
    expect(styles).toContain("@media (prefers-reduced-motion: reduce)");
    expect(styles).toContain("@media (forced-colors: active)");
    expect(styles).toContain(":focus-visible");
    expect(styles).toContain("outline-color: Highlight");
    expect(styles).toContain(".agreement-control");
    expect(styles).toContain(".choice-card");
  });
});
