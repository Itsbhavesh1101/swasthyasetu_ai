import { readFileSync } from "node:fs";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { readdirSync } from "node:fs";
import { describe, expect, it } from "vitest";

const applicationRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const browserSourceRoots = [
  join(applicationRoot, "app"),
  join(applicationRoot, "components"),
  join(applicationRoot, "lib", "onboarding", "client.ts"),
];

function sourceFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? sourceFiles(path) : [path];
  });
}

describe("P6-B browser boundaries", () => {
  const browserSource = browserSourceRoots
    .flatMap((path) => (extname(path) ? [path] : sourceFiles(path)))
    .filter((path) => [".ts", ".tsx"].includes(extname(path)))
    .map((path) => readFileSync(path, "utf8"))
    .join("\n");

  it("does not persist patient information in browser storage", () => {
    expect(browserSource).not.toMatch(/localStorage|sessionStorage|indexedDB|caches\./);
  });

  it("does not register a service worker or call backend routes from browser code", () => {
    expect(browserSource).not.toMatch(/serviceWorker|\/api\/v1\//);
    expect(browserSource).not.toContain("swasthyasetu_session_token");
  });
});
