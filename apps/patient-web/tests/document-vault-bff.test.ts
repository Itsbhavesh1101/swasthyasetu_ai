// @vitest-environment node
import { NextRequest } from "next/server";
import { afterEach, expect, it, vi } from "vitest";
import { GET, POST } from "../app/api/patient/documents/route";
import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../lib/onboarding/server";

const sessionId = "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1";
const patientId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";
const documentId = "3f0bb868-b00b-41c6-9335-f9c8b96ce7b3";
const bearer = "private-document-token";
const cookie = `${SESSION_ID_COOKIE}=${sessionId}; ${SESSION_TOKEN_COOKIE}=${bearer}`;
const item = {
  document_id: documentId,
  display_name: "report.pdf",
  mime_type: "application/pdf",
  byte_size: 12,
  created_at: "2026-11-03T14:00:00Z",
};

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

it("derives the patient document list and does not expose bearer or object keys", async () => {
  vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
  const backend = vi
    .fn()
    .mockResolvedValueOnce(Response.json({ patient_id: patientId }))
    .mockResolvedValueOnce(Response.json({ items: [item] }));
  vi.stubGlobal("fetch", backend);
  const response = await GET(
    new NextRequest("http://localhost:3000/api/patient/documents", { headers: { cookie } }),
  );
  const text = await response.text();
  expect(JSON.parse(text)).toMatchObject({
    state: "AUTHENTICATED",
    items: [{ documentId, displayName: "report.pdf" }],
  });
  expect(text).not.toContain(bearer);
  expect(text).not.toContain("object_key");
});

it("rejects cross-origin upload before backend access", async () => {
  const backend = vi.fn();
  vi.stubGlobal("fetch", backend);
  const form = new FormData();
  form.set("file", new File(["%PDF-x"], "report.pdf", { type: "application/pdf" }));
  const response = await POST(
    new NextRequest("http://localhost:3000/api/patient/documents", {
      method: "POST",
      headers: { cookie, origin: "https://attacker.invalid" },
      body: form,
    }),
  );
  expect(response.status).toBe(403);
  expect(backend).not.toHaveBeenCalled();
});

it("rejects an oversized upload before reading or forwarding the body", async () => {
  vi.stubEnv("SWASTHYASETU_BACKEND_URL", "http://127.0.0.1:8000");
  const backend = vi.fn().mockResolvedValueOnce(Response.json({ patient_id: patientId }));
  vi.stubGlobal("fetch", backend);
  const response = await POST(
    new NextRequest("http://localhost:3000/api/patient/documents", {
      method: "POST",
      headers: {
        cookie,
        origin: "http://localhost:3000",
        "content-type": "multipart/form-data; boundary=bounded",
        "content-length": String(11 * 1024 * 1024),
      },
      body: "--bounded--",
    }),
  );
  expect(response.status).toBe(413);
  expect(backend).toHaveBeenCalledTimes(1);
});
