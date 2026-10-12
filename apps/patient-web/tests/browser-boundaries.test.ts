import { readFileSync } from "node:fs";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { readdirSync } from "node:fs";
import { describe, expect, it } from "vitest";

const applicationRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoots = [join(applicationRoot, "app"), join(applicationRoot, "components")];

function sourceFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? sourceFiles(path) : [path];
  });
}

describe("P6-A browser boundaries", () => {
  const source = sourceRoots
    .flatMap(sourceFiles)
    .filter((path) => [".ts", ".tsx"].includes(extname(path)))
    .map((path) => readFileSync(path, "utf8"))
    .join("\n");

  it("does not persist patient information in browser storage", () => {
    expect(source).not.toMatch(/localStorage|sessionStorage|indexedDB|caches\./);
  });

  it("does not register a service worker or call backend patient endpoints", () => {
    expect(source).not.toMatch(/serviceWorker|\/api\/v1\/(sessions|consents|patients|encounters)/);
    expect(source).not.toMatch(/\bfetch\s*\(/);
  });
});
