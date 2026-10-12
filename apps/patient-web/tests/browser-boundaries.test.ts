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

describe("P6-C browser boundaries", () => {
  const browserSource = browserSourceRoots
    .flatMap((path) => (extname(path) ? [path] : sourceFiles(path)))
    .filter((path) => [".ts", ".tsx"].includes(extname(path)))
    .map((path) => readFileSync(path, "utf8"))
    .join("\n");

  it("does not persist patient information in browser storage", () => {
    expect(browserSource).not.toMatch(/localStorage|sessionStorage|indexedDB|caches\./);
  });

  it("keeps backend contracts and bearer names out of browser code", () => {
    expect(browserSource).not.toMatch(/\/api\/v1\//);
    expect(browserSource).not.toContain("swasthyasetu_session_token");
  });

  it("limits service-worker access to the registration boundary", () => {
    const filesWithServiceWorker = browserSourceRoots
      .flatMap((path) => (extname(path) ? [path] : sourceFiles(path)))
      .filter((path) => [".ts", ".tsx"].includes(extname(path)))
      .filter((path) => readFileSync(path, "utf8").includes("serviceWorker"));

    expect(filesWithServiceWorker).toEqual([
      join(applicationRoot, "components", "pwa-registration.tsx"),
    ]);
  });
});
