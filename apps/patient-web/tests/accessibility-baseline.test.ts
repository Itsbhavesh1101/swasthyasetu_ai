// @vitest-environment node

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const applicationRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const styles = readFileSync(join(applicationRoot, "app", "globals.css"), "utf8");

function cssVariable(name: string): string {
  const value = styles.match(new RegExp(`${name}:\\s*(#[0-9a-fA-F]{6})`))?.[1];
  if (!value) throw new Error(`Missing CSS color variable ${name}`);
  return value.toUpperCase();
}

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
  it("uses the approved patient indigo palette", () => {
    expect([
      cssVariable("--patient-canvas"),
      cssVariable("--patient-sidebar"),
      cssVariable("--patient-surface"),
      cssVariable("--patient-surface-strong"),
      cssVariable("--patient-primary"),
      cssVariable("--patient-muted"),
      cssVariable("--patient-text"),
    ]).toEqual(["#12141F", "#232739", "#383E5C", "#4F5580", "#7B81A8", "#AFB4CE", "#E4E6F0"]);
  });

  it.each([
    ["main text on canvas", "--patient-text", "--patient-canvas", 4.5],
    ["main text on surface", "--patient-text", "--patient-surface", 4.5],
    ["muted text on sidebar", "--patient-muted", "--patient-sidebar", 4.5],
    ["primary button", "--patient-canvas", "--patient-primary", 4.5],
    ["critical button", "#ffffff", "#a52a2a", 4.5],
    ["focus indicator", "--patient-text", "--patient-surface-strong", 3],
    ["disabled control", "#5c665f", "#e6eae7", 4.5],
  ])("passes contrast for %s", (_label, foreground, background, minimum) => {
    const foregroundColor = foreground.startsWith("--") ? cssVariable(foreground) : foreground;
    const backgroundColor = background.startsWith("--") ? cssVariable(background) : background;
    expect(contrast(foregroundColor, backgroundColor)).toBeGreaterThanOrEqual(minimum);
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

  it("keeps first-time profile tiles keyboard, motion, and small-screen safe", () => {
    expect(styles).toContain(".profile-wizard-card");
    expect(styles).toContain(".wizard-field input");
    expect(styles).toContain("min-height: 3.35rem");
    expect(styles).toContain("@media (max-width: 30rem)");
    expect(styles).toContain("transition: width 220ms ease");
  });
});
