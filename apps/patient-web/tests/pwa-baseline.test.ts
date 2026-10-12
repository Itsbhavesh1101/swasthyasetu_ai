// @vitest-environment node

import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import manifest from "../app/manifest";

const applicationRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const serviceWorker = readFileSync(join(applicationRoot, "public", "sw.js"), "utf8");

function pngDimensions(path: string): [number, number] {
  const png = readFileSync(path);
  expect(png.subarray(1, 4).toString()).toBe("PNG");
  return [png.readUInt32BE(16), png.readUInt32BE(20)];
}

describe("P6-C privacy-safe PWA baseline", () => {
  it("declares installable root-scope metadata and owned icons", () => {
    const value = manifest();
    expect(value).toMatchObject({
      name: "SwasthyaSetu Patient",
      short_name: "SwasthyaSetu",
      start_url: "/",
      scope: "/",
      display: "standalone",
      lang: "en",
    });
    expect(value.icons).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ src: "/icons/icon-192.png", sizes: "192x192" }),
        expect.objectContaining({ src: "/icons/icon-512.png", sizes: "512x512" }),
        expect.objectContaining({
          src: "/icons/icon-maskable-512.png",
          sizes: "512x512",
          purpose: "maskable",
        }),
      ]),
    );

    for (const icon of value.icons ?? []) {
      expect(existsSync(join(applicationRoot, "public", icon.src.replace(/^\//, "")))).toBe(true);
    }
    expect(pngDimensions(join(applicationRoot, "public", "icons", "icon-192.png"))).toEqual([
      192, 192,
    ]);
    expect(pngDimensions(join(applicationRoot, "public", "icons", "icon-512.png"))).toEqual([
      512, 512,
    ]);
  });

  it("uses an explicit generic-only shell allowlist", () => {
    expect(serviceWorker).toContain("const CACHE_NAME = `${CACHE_PREFIX}v1`");
    expect(serviceWorker).toContain('"/offline"');
    expect(serviceWorker).toContain('"/manifest.webmanifest"');
    expect(serviceWorker).toContain('"/icons/icon-192.png"');
    expect(serviceWorker).not.toMatch(/["'`]\/consent["'`]/);
    expect(serviceWorker).not.toMatch(/["'`]\/encounter["'`]/);
    expect(serviceWorker).not.toContain("clinical_intake");
    expect(serviceWorker).not.toContain("session_token");
  });

  it("bypasses APIs and mutations and uses network-only navigation with offline fallback", () => {
    expect(serviceWorker).toContain('request.method !== "GET"');
    expect(serviceWorker).toContain('url.pathname.startsWith("/api/")');
    expect(serviceWorker).toContain('request.mode === "navigate"');
    expect(serviceWorker).toContain('fetch(request).catch(() => caches.match("/offline"))');
    expect(serviceWorker).not.toMatch(/addEventListener\(["'](?:sync|push)["']/i);
  });

  it("deletes only obsolete SwasthyaSetu shell caches", () => {
    expect(serviceWorker).toContain("name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME");
    expect(serviceWorker).toContain("caches.delete(name)");
  });
});
